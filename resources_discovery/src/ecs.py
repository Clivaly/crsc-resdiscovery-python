import boto3
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.utils import create_empty_df, format_tags
from src.tags import get_ecs_tags

# Inicializa o cliente ECS da AWS
ECS_CLIENT = boto3.client('ecs')

def add_empty_cluster_info(cluster_name: str, services_info: list):
    """Adiciona informações de um cluster vazio à lista de serviços."""
    services_info.append({
        'Cluster Name': cluster_name,
        'Service Name': 'No services',
        'Desired Count': 'N/A',
        'Running Count': 'N/A',
        'Pending Count': 'N/A',
        'Memory': 'N/A',
        'CPU': 'N/A',
        'Min Capacity': 'N/A',
        'Max Capacity': 'N/A',
        'Capacity Provider': 'N/A',
        'Launch Type': 'N/A',
        'Tags': 'N/A'
    })

def fetch_service_details(cluster: str, service_arn: str):
    """Busca detalhes de um serviço específico em um cluster ECS."""
    try:
        service = ECS_CLIENT.describe_services(cluster=cluster, services=[service_arn])['services'][0]
        service_name = service['serviceName']
        capacity_provider_strategy = service.get('capacityProviderStrategy', [])
        launch_type = service.get('launchType', 'N/A')

        if capacity_provider_strategy:
            capacity_provider = capacity_provider_strategy[0].get('capacityProvider', 'N/A')
            base = capacity_provider_strategy[0].get('base', 'N/A')
            weight = capacity_provider_strategy[0].get('weight', 'N/A')
        else:
            capacity_provider = 'N/A'
            base = 'N/A'
            weight = 'N/A'

        tasks = ECS_CLIENT.list_tasks(cluster=cluster, serviceName=service_name)['taskArns']
        service_info = []

        if tasks:
            for task in tasks:
                try:
                    task_desc = ECS_CLIENT.describe_tasks(cluster=cluster, tasks=[task])['tasks'][0]
                    container_definitions = task_desc['containers']
                    for container in container_definitions:
                        tags = get_ecs_tags(service_arn)
                        formatted_tags = format_tags(tags)
                        service_info.append({
                            'Cluster Name': cluster.split('/')[-1],
                            'Service Name': service_name,
                            'Desired Count': service['desiredCount'],
                            'Running Count': service['runningCount'],
                            'Pending Count': service['pendingCount'],
                            'Memory': container.get('memory', 'N/A'),
                            'CPU': container.get('cpu', 'N/A'),
                            'Min Capacity': base,
                            'Max Capacity': weight,
                            'Capacity Provider': capacity_provider,
                            'Launch Type': launch_type,
                            'Tags': formatted_tags
                        })
                except Exception as e:
                    print(f'Error describing task {task}: {e}')
        else:
            tags = get_ecs_tags(service_arn)
            formatted_tags = format_tags(tags)
            service_info.append({
                'Cluster Name': cluster.split('/')[-1],
                'Service Name': service_name,
                'Desired Count': service['desiredCount'],
                'Running Count': service['runningCount'],
                'Pending Count': service['pendingCount'],
                'Memory': 'N/A',
                'CPU': 'N/A',
                'Min Capacity': base,
                'Max Capacity': weight,
                'Capacity Provider': capacity_provider,
                'Launch Type': launch_type,
                'Tags': formatted_tags
            })

        return service_info
    except Exception as e:
        print(f'Error retrieving service details for {service_arn}: {e}')
        return []

def get_ecs_services() -> pd.DataFrame:
    """Recupera informações de todos os serviços ECS em todos os clusters."""
    services_info = []
    processed_services = set()

    try:
        clusters = ECS_CLIENT.list_clusters()['clusterArns']
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_service = {}
            for cluster in clusters:
                service_arns = ECS_CLIENT.list_services(cluster=cluster)['serviceArns']
                if not service_arns:
                    add_empty_cluster_info(cluster.split('/')[-1], services_info)
                else:
                    for service_arn in service_arns:
                        if service_arn not in processed_services:
                            future = executor.submit(fetch_service_details, cluster, service_arn)
                            future_to_service[future] = service_arn
                            processed_services.add(service_arn)

            for future in as_completed(future_to_service):
                service_info = future.result()
                services_info.extend(service_info)

    except Exception as e:
        print(f'Error retrieving ECS services: {e}')
        return create_empty_df(['Error'])

    return pd.DataFrame(services_info) if services_info else create_empty_df(["No ECS services found"])