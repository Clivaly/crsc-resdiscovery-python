# src/apigateway.py
import boto3
import pandas as pd
from src.utils.utils import create_empty_df, format_tags
from src.tags import get_apigateway_tags

def get_api_gateways():
    client = boto3.client('apigateway')
    apis = []
    try:
        response = client.get_rest_apis()
        for api in response.get('items', []):
            api_id = api['id']
            tags = get_apigateway_tags(api_id)
            formatted_tags = format_tags(tags)
            apis.append({
                "API Name": api['name'],
                "API ID": api_id,
                "Description": api.get('description', 'N/A'),
                "Created Date": api['createdDate'].strftime("%Y-%m-%d %H:%M:%S"),
                "Tags": formatted_tags
            })
    except Exception as e:
        print(f"Error retrieving API Gateways: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(apis) if apis else create_empty_df(["No API Gateways found"])