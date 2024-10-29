import boto3
import pandas as pd
from datetime import timezone
from src.utils.utils import check_idle_state, create_empty_df


def get_rds_instances():
    rds_client = boto3.client('rds')
    instances = []
    try:
        response = rds_client.describe_db_instances()
        for instance in response['DBInstances']:
            launch_time = instance['InstanceCreateTime'].replace(tzinfo=timezone.utc)
            idle_days = check_idle_state(launch_time)
            instance_info = {
                "DBInstance Identifier": instance['DBInstanceIdentifier'],
                "DBInstance Class": instance['DBInstanceClass'],
                "Engine": instance['Engine'],
                "Status": instance['DBInstanceStatus'],
                "Allocated Storage (GB)": instance['AllocatedStorage'],
                "Idle Days": idle_days,
                "Provisioning Type": instance.get('StorageType', 'N/A'),
                "State": instance['DBInstanceStatus'] # Adding state (stopped or running)
            }
            instances.append(instance_info)
    except Exception as e:
        print(f"Error retrieving RDS instances: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(instances) if instances else create_empty_df(["No RDS instances found"])

def get_rds_aurora_instances():
    rds_client = boto3.client('rds')
    instances = []
    try:
        response = rds_client.describe_db_clusters()
        for cluster in response['DBClusters']:
            launch_time = cluster['ClusterCreateTime'].replace(tzinfo=timezone.utc)
            idle_days = check_idle_state(launch_time)
            instances.append({
                "DBCluster Identifier": cluster['DBClusterIdentifier'],
                "Status": cluster['Status'],
                "Engine": cluster['Engine'],
                "Idle Days": idle_days,
                "Provisioning Type": cluster.get('EngineMode', 'N/A'),
                "State": cluster['Status'] # Adding state (stopped or running)
            })
    except Exception as e:
        print(f"Error retrieving RDS Aurora instances: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(instances) if instances else create_empty_df(["No RDS Aurora instances found"])