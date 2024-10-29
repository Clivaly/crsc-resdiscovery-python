import boto3
import pandas as pd
from src.utils.utils import create_empty_df, format_date


def get_lambda_functions():
    lambda_client = boto3.client('lambda')
    functions = []
    try:
        paginator = lambda_client.get_paginator('list_functions')
        for page in paginator.paginate():
            for function in page['Functions']:
                functions.append({
                    "Function Name": function['FunctionName'],
                    "Runtime": function['Runtime'],
                    "Last Modified": format_date(function['LastModified'])
                })
    except Exception as e:
        print(f"Error retrieving Lambda functions: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(functions) if functions else create_empty_df(["No Lambda functions found"])