from datetime import datetime, timezone
import pandas as pd

def format_date(date_str):
    """Formata a data no formato dia-mês-ano."""
    return pd.to_datetime(date_str).strftime("%d-%m-%Y") if date_str else ''

def check_idle_state(launch_time):
    return (datetime.now(timezone.utc) - launch_time).days if launch_time else 0

def create_empty_df(columns):
    return pd.DataFrame(columns=columns)

def remove_duplicates(df, column_name):
    """Remove duplicates based on a specific column name."""
    return df.drop_duplicates(subset=[column_name])

def convert_lists_to_strings(df):
    """Convert list columns to strings for a given DataFrame."""
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)
    return df

def save_to_excel(filename, **services):
    try:
        # Convert list columns to strings and remove duplicates for all dataframes in services
        for service_name, df in services.items():
            df = convert_lists_to_strings(df)
            if service_name == 'ecs':
                df = remove_duplicates(df, "Service Name")
            services[service_name] = df

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for service_name, df in services.items():
                df.to_excel(writer, sheet_name=service_name.upper(), index=False)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")

def format_tags(tags):
    """Format tags dictionary into a multi-line string with commas."""
    formatted_tags = [f"{key}: {value}," for key, value in tags.items()]
    if formatted_tags:
        formatted_tags[-1] = formatted_tags[-1].rstrip(',')  # Remove the comma from the last item
    return '\n'.join(formatted_tags)
