import boto3
import pandas as pd
import subprocess
import json
import requests
import urllib3
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from src.utils.utils import create_empty_df, format_service_info, format_tags
from src.tags import get_eks_tags

# Desativar avisos de segurança do urllib3 e requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

# Configurar a lógica de repetição para as solicitações HTTP
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

def get_eks_clusters():
    eks_client = boto3.client('eks')
    clusters_info = []
    try:
        clusters = eks_client.list_clusters()['clusters']
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_cluster_info, eks_client, cluster_name) for cluster_name in clusters]
            for future in as_completed(futures):
                cluster_services_info = future.result()
                if cluster_services_info:
                    clusters_info.extend(cluster_services_info)
    except Exception as e:
        print(f"Error retrieving EKS clusters: {e}")
    return pd.DataFrame(clusters_info) if clusters_info else create_empty_df(["No EKS clusters found"])

def get_cluster_info(eks_client, cluster_name):
    try:
        cluster_info = eks_client.describe_cluster(name=cluster_name)['cluster']
        nodegroups = eks_client.list_nodegroups(clusterName=cluster_name)['nodegroups']
        fargate_profiles = eks_client.list_fargate_profiles(clusterName=cluster_name)['fargateProfileNames']
        compute_type = "EC2" if nodegroups else "Fargate" if fargate_profiles else "Unknown"
        services_info = []
        namespaces = list_namespaces(cluster_info['name'])
        cluster_tags = get_eks_tags(cluster_name)
        formatted_tags = format_tags(cluster_tags)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(list_services, cluster_info['name'], namespace) for namespace in namespaces]
            for future in as_completed(futures):
                services = future.result()
                for service in services:
                    services_info.append({
                        "Cluster Name": cluster_info['name'],
                        "Status": cluster_info['status'],
                        "Version": cluster_info['version'],
                        "Endpoint": cluster_info['endpoint'],
                        "Role ARN": cluster_info['roleArn'],
                        "Created At": cluster_info['createdAt'].strftime('%Y-%m-%d %H:%M:%S'),
                        "Compute Type": compute_type,
                        "Namespace": service['metadata']['namespace'],
                        "Service Name": service['metadata']['name'],
                        "Service Type": service['spec']['type'],
                        "Cluster IP": service['spec']['clusterIP'],
                        "External IPs": ', '.join(service['spec'].get('externalIPs', [])),
                        "Ports": ', '.join(map(str, [port['port'] for port in service['spec']['ports']])),
                        "Cluster Tags": formatted_tags,
                        # "Service Labels": service.get('labels', {})  # Adicione as labels do serviço aqui
                    })
        return services_info
    except Exception as e:
        print(f"Error retrieving cluster info for {cluster_name}: {e}")
    return None

def list_namespaces(cluster_name):
    try:
        token = get_eks_token(cluster_name)
    except Exception as e:
        print(f"Error getting token: {e}")
        return []
    cluster_info = boto3.client('eks').describe_cluster(name=cluster_name)['cluster']
    endpoint = cluster_info['endpoint']
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    response = http.get(f'{endpoint}/api/v1/namespaces', headers=headers, verify=False)
    if response.status_code == 200:
        return [ns['metadata']['name'] for ns in response.json()['items']]
    else:
        print(f"Error retrieving namespaces: {response.status_code} {response.text}")
    return []

def list_services(cluster_name, namespace):
    try:
        token = get_eks_token(cluster_name)
    except Exception as e:
        print(f"Error getting token: {e}")
        return []
    cluster_info = boto3.client('eks').describe_cluster(name=cluster_name)['cluster']
    endpoint = cluster_info['endpoint']
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    response = http.get(f'{endpoint}/api/v1/namespaces/{namespace}/services', headers=headers, verify=False)
    if response.status_code == 200:
        services = response.json()['items']
        for service in services:
            service['labels'] = service['metadata'].get('labels', {})
        return services
    else:
        print(f"Error retrieving services: {response.status_code} {response.text}")
    return []

def get_eks_token(cluster_name):
    result = subprocess.run(
        ['aws', 'eks', 'get-token', '--cluster-name', cluster_name],
        capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)['status']['token']