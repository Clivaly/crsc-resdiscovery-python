import boto3

def get_tags(resource_arn):
    """Retrieve tags for a given AWS resource."""
    client = boto3.client('resourcegroupstaggingapi')
    response = client.get_resources(
        ResourceARNList=[resource_arn]
    )
    tags = {}
    if response['ResourceTagMappingList']:
        tags = {tag['Key']: tag['Value'] for tag in response['ResourceTagMappingList'][0]['Tags']}
    return tags

def get_ec2_tags(instance_id):
    ec2_client = boto3.client('ec2')
    region = ec2_client.meta.region_name
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    resource_arn = f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}"
    return get_tags(resource_arn)

def get_rds_tags(db_instance_arn):
    return get_tags(db_instance_arn)

def get_aurora_tags(cluster_arn):
    return get_tags(cluster_arn)

def get_ecs_tags(cluster_arn):
    return get_tags(cluster_arn)

def get_glue_tags(job_name):
    return get_tags(job_name)

def get_kinesis_tags(stream_arn):
    return get_tags(stream_arn)

def get_lambda_tags(function_arn):
    return get_tags(function_arn)