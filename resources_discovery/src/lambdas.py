import boto3
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.utils import create_empty_df, format_date, format_tags
from src.tags import get_lambda_tags

def fetch_function_tags(function_arn):
    try:
        tags = get_lambda_tags(function_arn)
        return format_tags(tags)
    except Exception as e:
        print(f"Error retrieving tags for {function_arn}: {e}")
        return "Error"

def get_lambda_functions():
    lambda_client = boto3.client('lambda')
    functions = []
    try:
        paginator = lambda_client.get_paginator('list_functions')
        function_arns = []
        for page in paginator.paginate():
            for function in page['Functions']:
                function_arns.append(function['FunctionArn'])
                functions.append({
                    "Function Name": function['FunctionName'],
                    "Runtime": function['Runtime'],
                    "Last Modified": format_date(function['LastModified']),
                    "FunctionArn": function['FunctionArn'],  # Store the ARN for later use
                    "Tags": ""  # Placeholder for tags
                })
        
        # Reduce the number of threads to avoid throttling
        max_threads = 10  # Adjust this number based on your needs and API rate limits
        with ThreadPoolExecutor(max_threads) as executor:
            future_to_arn = {executor.submit(fetch_function_tags, arn): arn for arn in function_arns}
            for future in as_completed(future_to_arn):
                arn = future_to_arn[future]
                try:
                    tags = future.result()
                    for function in functions:
                        if function['FunctionArn'] == arn:
                            function['Tags'] = tags
                            break
                except Exception as e:
                    print(f"Error processing tags for {arn}: {e}")
        
        # Remove the 'FunctionArn' key from the final output
        for function in functions:
            function.pop('FunctionArn', None)
    
    except Exception as e:
        print(f"Error retrieving Lambda functions: {e}")
        return create_empty_df(["Error"])
    
    return pd.DataFrame(functions) if functions else create_empty_df(["No Lambda functions found"])