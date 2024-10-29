import boto3
import pandas as pd
from src.utils.utils import create_empty_df, format_date


def get_glue_jobs():
    glue_client = boto3.client('glue')
    jobs = []
    try:
        response = glue_client.get_jobs()
        for job in response['Jobs']:
            jobs.append({
                "Job Name": job['Name'],
                "Worker Type": job.get('WorkerType', 'N/A'),
                "Last Modified": format_date(job['LastModifiedOn'].strftime("%Y-%m-%dT%H:%M:%SZ")),
            })
    except Exception as e:
        print(f"Error retrieving Glue jobs: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(jobs) if jobs else create_empty_df(["No Glue jobs found"])