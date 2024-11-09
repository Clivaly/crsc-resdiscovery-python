import boto3
import pandas as pd
from src.utils.utils import create_empty_df, format_date, format_tags
from src.tags import get_glue_tags

def get_glue_jobs():
    glue_client = boto3.client('glue')
    jobs = []
    try:
        response = glue_client.get_jobs()
        for job in response['Jobs']:
            job_name = job['Name']
            tags = get_glue_tags(job_name)
            formatted_tags = format_tags(tags)
            jobs.append({
                "Job Name": job_name,
                "Worker Type": job.get('WorkerType', 'N/A'),
                "Last Modified": format_date(job['LastModifiedOn'].strftime("%Y-%m-%dT%H:%M:%SZ")),
                "Tags": formatted_tags
            })
    except Exception as e:
        print(f"Error retrieving Glue jobs: {e}")
        return create_empty_df(["Error"])
    return pd.DataFrame(jobs) if jobs else create_empty_df(["No Glue jobs found"])