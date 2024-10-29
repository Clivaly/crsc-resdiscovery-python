import boto3
import pandas as pd
from src.utils.utils import create_empty_df, format_date


def get_kinesis_streams():
    kinesis_client = boto3.client('kinesis')
    streams = []
    try:
        response = kinesis_client.list_streams()
        for stream_name in response['StreamNames']:
            stream_info = kinesis_client.describe_stream(StreamName=stream_name)['StreamDescription']
            mode = 'On-Demand' if stream_info.get('StreamModeDetails', {}).get('StreamMode') == 'ON_DEMAND' else 'Provisioned'
            streams.append({
                "Stream Name": stream_info['StreamName'],
                "Stream ARN": stream_info['StreamARN'],
                "Status": stream_info['StreamStatus'],
                "Shards": len(stream_info['Shards']),
                "Retention Period Hours": stream_info['RetentionPeriodHours'],
                "Creation Time": format_date(stream_info['StreamCreationTimestamp'].strftime("%Y-%m-%dT%H:%M:%SZ")),
                "Mode": mode
            })
    except Exception as e:
        print(f"Error retrieving Kinesis streams: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(streams) if streams else create_empty_df(["No Kinesis streams found"])