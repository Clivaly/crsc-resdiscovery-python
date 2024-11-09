# elb.py
import boto3
import pandas as pd
from src.utils.utils import create_empty_df, format_tags
from src.tags import get_elb_tags

def get_load_balancers():
    elbv2_client = boto3.client('elbv2')
    load_balancers = []
    try:
        response = elbv2_client.describe_load_balancers()
        for lb in response['LoadBalancers']:
            lb_arn = lb['LoadBalancerArn']
            tags = get_elb_tags(lb_arn)
            formatted_tags = format_tags(tags)
            lb_info = {
                "Load Balancer Name": lb['LoadBalancerName'],
                "Type": lb['Type'],
                "State": lb['State']['Code'],
                "DNS Name": lb['DNSName'],
                "Tags": formatted_tags
            }
            listeners = elbv2_client.describe_listeners(LoadBalancerArn=lb_arn)['Listeners']
            lb_info["Listeners"] = [listener['ListenerArn'] for listener in listeners] if listeners else "No listeners"
            target_groups = elbv2_client.describe_target_groups(LoadBalancerArn=lb_arn)['TargetGroups']
            lb_info["Targets"] = [tg['TargetGroupArn'] for tg in target_groups] if target_groups else "No targets"
            load_balancers.append(lb_info)
    except Exception as e:
        print(f"Error retrieving Load Balancers: {e}")
        return create_empty_df(["Error"])

    # Especificar a ordem das colunas
    columns_order = ["Load Balancer Name", "Type", "State", "DNS Name", "Listeners", "Targets", "Tags"]
    df = pd.DataFrame(load_balancers, columns=columns_order)
    return df if not df.empty else create_empty_df(columns_order)