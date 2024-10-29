import boto3
import pandas as pd
from src.utils.utils import create_empty_df


def get_ecs_services():
    ecs_client = boto3.client('ecs')
    services_info = []
    processed_services = set() # Set to track processed services by name globally
    try:
        clusters = ecs_client.list_clusters()['clusterArns']
        for cluster in clusters:
            service_arns = ecs_client.list_services(cluster=cluster)['serviceArns']
            if not service_arns: # If no services, add the cluster with a note that it has no services
                services_info.append({
                    "Cluster Name": cluster.split('/')[-1],
                    "Service Name": "No services",
                    "Desired Count": "N/A",
                    "Running Count": "N/A",
                    "Pending Count": "N/A",
                    "Memory": "N/A",
                    "CPU": "N/A",
                    "Min Capacity": "N/A",
                    "Max Capacity": "N/A",
                    "Capacity Provider": "N/A",
                    "Launch Type": "N/A"
                })
            for service_arn in service_arns:
                service = ecs_client.describe_services(cluster=cluster, services=[service_arn])['services'][0]
                service_name = service['serviceName']
                if service_name in processed_services:
                    continue # Skip if service already processed
                processed_services.add(service_name)
                # Get capacity provider strategy or launch type
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
                tasks = ecs_client.list_tasks(cluster=cluster, serviceName=service['serviceName'])['taskArns']
                if tasks:
                    for task in tasks:
                        try:
                            task_desc = ecs_client.describe_tasks(cluster=cluster, tasks=[task])['tasks'][0]
                            container_definitions = task_desc['containers']
                            for container in container_definitions:
                                services_info.append({
                                    "Cluster Name": cluster.split('/')[-1],
                                    "Service Name": service['serviceName'],
                                    "Desired Count": service['desiredCount'],
                                    "Running Count": service['runningCount'],
                                    "Pending Count": service['pendingCount'],
                                    "Memory": container.get('memory', 'N/A'),
                                    "CPU": container.get('cpu', 'N/A'),
                                    "Min Capacity": base,
                                    "Max Capacity": weight,
                                    "Capacity Provider": capacity_provider,
                                    "Launch Type": launch_type
                                })
                        except Exception as e:
                            print(f"Error describing task {task}: {e}")
                else:
                    services_info.append({
                        "Cluster Name": cluster.split('/')[-1],
                        "Service Name": service['serviceName'],
                        "Desired Count": service['desiredCount'],
                        "Running Count": service['runningCount'],
                        "Pending Count": service['pendingCount'],
                        "Memory": "N/A",
                        "CPU": "N/A",
                        "Min Capacity": base,
                        "Max Capacity": weight,
                        "Capacity Provider": capacity_provider,
                        "Launch Type": launch_type,
                        "Módulo IAC": "",
                        "Versão do módulo == v0.33.x": "",
                        "Verãso Atual do HN8": "",
                        "Repositório": "",
                        "Observações": ""
                    })
    except Exception as e:
        print(f"Error retrieving ECS services: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(services_info) if services_info else create_empty_df(["No ECS services found"])