import boto3
import pandas as pd
from datetime import datetime, timezone
from src.utils.utils import check_idle_state, create_empty_df, format_date, format_tags
from src.tags import get_ec2_tags

def check_ami_expiration(ami):
    if 'CreationDate' in ami:
        creation_date = pd.to_datetime(ami['CreationDate']).replace(tzinfo=timezone.utc)
        days_old = (datetime.now(timezone.utc) - creation_date).days
        if days_old > 180:
            return days_old, 'Expired'
        else:
            return 90 - days_old, 'Valid'
    return None, 'N/A'

def get_ec2_instances():
    ec2_client = boto3.client('ec2')
    instances = []
    try:
        response = ec2_client.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                state = instance['State']['Name']
                if state in ['running', 'stopped']:
                    ami_info = ec2_client.describe_images(ImageIds=[instance['ImageId']])['Images'][0]
                    expiration_days, status = check_ami_expiration(ami_info)
                    launch_time = instance['LaunchTime'].replace(tzinfo=timezone.utc)
                    idle_days = check_idle_state(launch_time)
                    tags = get_ec2_tags(instance['InstanceId'])
                    formatted_tags = format_tags(tags)
                    instance_info = {
                        "Instance ID": instance['InstanceId'],
                        "Instance Type": instance['InstanceType'],
                        "State": state,
                        "Launch Time": format_date(launch_time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                        "AMI Name": ami_info['Name'],
                        "AMI ID": ami_info['ImageId'],
                        "AMI Status": status,
                        "Days Until Expiration": expiration_days if status == 'Valid' else 0,
                        "Idle Days": idle_days,
                        "Instance Cycle": instance.get('InstanceLifecycle', 'On-Demand'),
                        "Tags": formatted_tags
                    }
                    instances.append(instance_info)
    except Exception as e:
        print(f"Error retrieving EC2 instances: {e}")
    return pd.DataFrame(instances) if instances else create_empty_df(["No EC2 instances found"])