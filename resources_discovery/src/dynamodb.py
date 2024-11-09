import boto3
import pandas as pd
from src.utils.utils import create_empty_df, format_tags
from src.tags import get_dynamodb_tags

def get_dynamodb_tables():
    dynamodb_client = boto3.client('dynamodb')
    tables = []
    try:
        response = dynamodb_client.list_tables()
        for table_name in response['TableNames']:
            table_info = dynamodb_client.describe_table(TableName=table_name)['Table']
            tags = get_dynamodb_tags(table_info['TableArn'])
            formatted_tags = format_tags(tags)
            tables.append({
                "Table Name": table_info['TableName'],
                "Provisioned Throughput": table_info['ProvisionedThroughput']['ReadCapacityUnits'],
                "Status": table_info['TableStatus'],
                "Billing Mode": table_info.get('BillingModeSummary', {}).get('BillingMode', 'N/A'),
                "Tags": formatted_tags
            })
    except Exception as e:
        print(f"Error retrieving DynamoDB tables: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(tables) if tables else create_empty_df(["No DynamoDB tables found"])