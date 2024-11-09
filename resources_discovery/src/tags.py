import boto3
import random
import time


def get_tags(resource_arn):
    """Retrieve tags for a given AWS resource."""
    client = boto3.client('resourcegroupstaggingapi')
    retries = 50  # Aumentar o número de tentativas
    for i in range(retries):
        try:
            response = client.get_resources(ResourceARNList=[resource_arn])
            tags = {}
            if response['ResourceTagMappingList']:
                tags = {tag['Key']: tag['Value'] for tag in response['ResourceTagMappingList'][0]['Tags']}
            return tags
        except client.exceptions.ThrottledException as e:
            if i < retries - 1:
                sleep_time = (2 ** i) + random.uniform(0, 10)  # Aumentar o tempo de espera
                print(f'\nThrottled. Retrying in {sleep_time:.2f} seconds...')
                time.sleep(sleep_time)
            else:
                print(f'Error retrieving tags for {resource_arn}: {e}')
        except Exception as e:
            print(f'Error retrieving tags for {resource_arn}: {e}')
            return {}
    return {}


def get_ec2_tags(instance_id):
    ec2_client = boto3.client('ec2')
    region = ec2_client.meta.region_name
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    resource_arn = f'arn:aws:ec2:{region}:{account_id}:instance/{instance_id}'
    return get_tags(resource_arn)


def get_rds_tags(db_instance_arn):
    return get_tags(db_instance_arn)


def get_aurora_tags(cluster_arn):
    return get_tags(cluster_arn)


def get_dynamodb_tags(table_arn):
    return get_tags(table_arn)


def get_ecs_tags(cluster_arn):
    return get_tags(cluster_arn)


def get_glue_tags(job_name):
    glue_client = boto3.client('glue')
    region = glue_client.meta.region_name
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    resource_arn = f'arn:aws:glue:{region}:{account_id}:job/{job_name}'
    return get_tags(resource_arn)


def get_kinesis_tags(stream_arn):
    return get_tags(stream_arn)


def get_lambda_tags(function_arn):
    return get_tags(function_arn)


def get_elb_tags(load_balancer_arn):
    return get_tags(load_balancer_arn)


def get_asg_tags(instance_id):
    ec2_client = boto3.client('ec2')
    region = ec2_client.meta.region_name
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    resource_arn = f'arn:aws:ec2:{region}:{account_id}:instance/{instance_id}'
    return get_tags(resource_arn)


def get_eks_tags(cluster_name):
    eks_client = boto3.client('eks')
    region = eks_client.meta.region_name
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    resource_arn = f'arn:aws:eks:{region}:{account_id}:cluster/{cluster_name}'
    return get_tags(resource_arn)


def get_sqs_tags(queue_arn):
    return get_tags(queue_arn)


def get_apigateway_tags(api_id):
    client = boto3.client('apigateway')
    region = client.meta.region_name
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    resource_arn = f'arn:aws:apigateway:{region}::/restapis/{api_id}'
    return get_tags(resource_arn)