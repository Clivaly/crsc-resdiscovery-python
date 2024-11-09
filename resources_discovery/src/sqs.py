import boto3
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.utils import create_empty_df, format_date_from_timestamp, format_tags
from src.tags import get_tags

def format_size(bytes_size):
    if bytes_size < 1024:
        return f"{bytes_size} bytes"
    elif bytes_size < 1024**2:
        return f"{bytes_size / 1024:.2f} KB"
    else:
        return f"{bytes_size / 1024**2:.2f} MB"

def format_time_period(seconds):
    if seconds < 3600:
        return f"{seconds} seconds ({seconds // 60} min)"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{seconds} seconds ({hours} hr {minutes} min)"

def get_sqs_queues():
    sqs_client = boto3.client('sqs')
    queues_info = []
    max_threads = 20  # Ajuste este valor conforme necessário

    try:
        response = sqs_client.list_queues()
        queue_urls = response.get('QueueUrls', [])

        with ThreadPoolExecutor(max_threads) as executor:
            future_to_queue = {executor.submit(get_queue_attributes, sqs_client, queue_url): queue_url for queue_url in queue_urls}
            for future in as_completed(future_to_queue):
                try:
                    queue_info = future.result()
                    if queue_info:
                        queues_info.append(queue_info)
                except Exception as e:
                    print(f"Error processing queue: {e}")

    except Exception as e:
        print(f"Error retrieving SQS queues: {e}")
        return create_empty_df(["Error"])

    return pd.DataFrame(queues_info) if queues_info else create_empty_df(["No SQS queues found"])

def get_queue_attributes(sqs_client, queue_url):
    try:
        queue_attributes = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn', 'All'])['Attributes']
        queue_arn = queue_attributes['QueueArn']
        created_timestamp = format_date_from_timestamp(queue_attributes.get('CreatedTimestamp'))
        last_modified_timestamp = format_date_from_timestamp(queue_attributes.get('LastModifiedTimestamp'))
        tags = get_tags(queue_arn)
        formatted_tags = format_tags(tags)
        queue_name = queue_url.split('/')[-1]
        redrive_policy = queue_attributes.get('RedrivePolicy', None)
        is_dlq = 'Yes' if redrive_policy else 'No'
        visibility_timeout = queue_attributes.get('VisibilityTimeout', 'N/A')
        if visibility_timeout != 'N/A':
            visibility_timeout = format_time_period(int(visibility_timeout))
        message_retention_period = queue_attributes.get('MessageRetentionPeriod', 'N/A')
        if message_retention_period != 'N/A':
            message_retention_period = format_time_period(int(message_retention_period))
        maximum_message_size = queue_attributes.get('MaximumMessageSize', 'N/A')
        if maximum_message_size != 'N/A':
            maximum_message_size = format_size(int(maximum_message_size))
        receive_message_wait_time = queue_attributes.get('ReceiveMessageWaitTimeSeconds', 'N/A')
        queue_type = 'FIFO' if queue_attributes.get('FifoQueue') == 'true' else 'Standard'
        delay_seconds = queue_attributes.get('DelaySeconds', 'N/A')
        content_based_deduplication = queue_attributes.get('ContentBasedDeduplication', 'N/A')

        queue_info = {
            "Queue Name": queue_name,
            "Queue URL": queue_url,
            "Queue ARN": queue_arn,
            "Approximate Number of Messages": queue_attributes.get('ApproximateNumberOfMessages', 'N/A'),
            "Created Timestamp": created_timestamp,
            "Last Modified Timestamp": last_modified_timestamp,
            "Is DLQ": is_dlq,
            "Visibility Timeout": visibility_timeout,
            "Message Retention Period": message_retention_period,
            "Maximum Message Size": maximum_message_size,
            "Receive Message Wait Time": receive_message_wait_time,
            "Queue Type": queue_type,
            "Delay Seconds": delay_seconds,
            "Content-Based Deduplication": content_based_deduplication,
            "Tags": formatted_tags
        }

        return queue_info

    except Exception as e:
        print(f"Error retrieving attributes for {queue_url}: {e}")
        return None