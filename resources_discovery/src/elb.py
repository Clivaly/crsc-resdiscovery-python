import boto3
import pandas as pd
from src.utils.utils import create_empty_df


def get_load_balancers():
    elbv2_client = boto3.client('elbv2')
    load_balancers = []
    try:
        response = elbv2_client.describe_load_balancers()
        for lb in response['LoadBalancers']:
            lb_info = {
                "Load Balancer Name": lb['LoadBalancerName'],
                "Type": lb['Type'],
                "State": lb['State']['Code'],
                "DNS Name": lb['DNSName'],
            }
            listeners = elbv2_client.describe_listeners(LoadBalancerArn=lb['LoadBalancerArn'])['Listeners']
            lb_info["Listeners"] = [listener['ListenerArn'] for listener in listeners] if listeners else "No listeners"
            target_groups = elbv2_client.describe_target_groups(LoadBalancerArn=lb['LoadBalancerArn'])['TargetGroups']
            lb_info["Targets"] = [tg['TargetGroupArn'] for tg in target_groups] if target_groups else "No targets"
            load_balancers.append(lb_info)
    except Exception as e:
        print(f"Error retrieving Load Balancers: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(load_balancers) if load_balancers else create_empty_df(["No Load Balancers found"])