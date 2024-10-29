import boto3
import pandas as pd
from datetime import timezone
from src.utils.utils import check_idle_state, create_empty_df

def get_ebs_volumes():
    ec2_client = boto3.client('ec2')
    volumes = []
    try:
        response = ec2_client.describe_volumes()
        for volume in response['Volumes']:
            if volume['State'] == 'available': # Volume detached
                launch_time = volume['CreateTime'].replace(tzinfo=timezone.utc)
                idle_days = check_idle_state(launch_time)
                volume_info = {
                    "Volume ID": volume['VolumeId'],
                    "Size (GB)": volume['Size'],
                    "State": volume['State'],
                    "Idle Days": idle_days,
                }
                volumes.append(volume_info)
    except Exception as e:
        print(f"Error retrieving EBS volumes: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(volumes) if volumes else create_empty_df(["No EBS volumes found"])