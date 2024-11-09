import boto3
import pandas as pd
from src.utils.utils import create_empty_df, format_tags
from src.tags import get_asg_tags

def get_asg_instances():
    asg_client = boto3.client('autoscaling')
    asg_info = []
    try:
        response = asg_client.describe_auto_scaling_groups()
        for group in response['AutoScalingGroups']:
            for instance in group['Instances']:
                instance_id = instance['InstanceId']
                tags = get_asg_tags(instance_id)
                formatted_tags = format_tags(tags)
                asg_info.append({
                    "Auto Scaling Group Name": group['AutoScalingGroupName'],
                    "Instance ID": instance_id,
                    "Desired Capacity": group['DesiredCapacity'],
                    "Min Size": group['MinSize'],
                    "Max Size": group['MaxSize'],
                    "Instance Type": instance['InstanceType'],
                    "Spot Instance": instance.get('InstanceLifecycle', 'Regular'),
                    "Tags": formatted_tags
                })
    except Exception as e:
        print(f"Error retrieving ASG instances: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(asg_info) if asg_info else create_empty_df(["No ASG instances found"])