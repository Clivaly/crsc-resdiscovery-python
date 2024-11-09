import boto3
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.utils import create_empty_df, format_date, format_tags
from src.tags import get_kinesis_tags

def fetch_stream_tags(stream_arn):
    try:
        tags = get_kinesis_tags(stream_arn)
        return format_tags(tags)
    except Exception as e:
        print(f"Error retrieving tags for {stream_arn}: {e}")
        return "Error"

def get_kinesis_streams():
    kinesis_client = boto3.client('kinesis')
    streams = []
    try:
        response = kinesis_client.list_streams()
        stream_arns = []
        for stream_name in response['StreamNames']:
            stream_info = kinesis_client.describe_stream(StreamName=stream_name)['StreamDescription']
            mode = 'On-Demand' if stream_info.get('StreamModeDetails', {}).get('StreamMode') == 'ON_DEMAND' else 'Provisioned'
            stream_arn = stream_info['StreamARN']
            stream_arns.append(stream_arn)
            streams.append({
                "Stream Name": stream_info['StreamName'],
                "Stream ARN": stream_arn,
                "Status": stream_info['StreamStatus'],
                "Shards": len(stream_info['Shards']),
                "Retention Period Hours": stream_info['RetentionPeriodHours'],
                "Creation Time": format_date(stream_info['StreamCreationTimestamp'].strftime("%Y-%m-%dT%H:%M:%SZ")),
                "Mode": mode,
                "Tags": ""  # Placeholder for tags
            })

        # Increase the number of threads max_threads
        max_threads = 10  # Adjust this number based on your needs and API rate limits
        with ThreadPoolExecutor(max_threads) as executor:
            future_to_arn = {executor.submit(fetch_stream_tags, arn): arn for arn in stream_arns}
            for future in as_completed(future_to_arn):
                arn = future_to_arn[future]
                try:
                    tags = future.result()
                    for stream in streams:
                        if stream['Stream ARN'] == arn:
                            stream['Tags'] = tags
                            break
                except Exception as e:
                    print(f"Error processing tags for {arn}: {e}")

        # Remove the 'Stream ARN' key from the final output
        for stream in streams:
            stream.pop('Stream ARN', None)

    except Exception as e:
        print(f"Error retrieving Kinesis streams: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(streams) if streams else create_empty_df(["No Kinesis streams found"])