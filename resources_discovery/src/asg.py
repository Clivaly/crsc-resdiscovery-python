import boto3
import pandas as pd
from src.utils.utils import create_empty_df


def get_asg_instances():
    asg_client = boto3.client('autoscaling')
    asg_info = []
    try:
        response = asg_client.describe_auto_scaling_groups()
        for group in response['AutoScalingGroups']:
            for instance in group['Instances']:
                asg_info.append({
                    "Auto Scaling Group Name": group['AutoScalingGroupName'],
                    "Instance ID": instance['InstanceId'],
                    "Desired Capacity": group['DesiredCapacity'],
                    "Min Size": group['MinSize'],
                    "Max Size": group['MaxSize'],
                    "Instance Type": instance['InstanceType'],
                    "Spot Instance": instance.get('InstanceLifecycle', 'Regular')
                })
    except Exception as e:
        print(f"Error retrieving ASG instances: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(asg_info) if asg_info else create_empty_df(["No ASG instances found"])