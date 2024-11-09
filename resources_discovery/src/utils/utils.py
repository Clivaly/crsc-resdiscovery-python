from datetime import datetime, timezone
import pandas as pd

def format_date(date_str):
    """Formata a data no formato dia-mês-ano."""
    return pd.to_datetime(date_str).strftime("%d-%m-%Y") if date_str else ''

def format_date_from_timestamp(timestamp):
    """Converte um timestamp Unix para o formato dia-mês-ano."""
    if timestamp:
        # Converte o timestamp para um objeto datetime
        date_obj = datetime.fromtimestamp(float(timestamp))
        # Formata a data usando a função format_date
        return format_date(date_obj)
    return ''

def check_idle_state(launch_time):
    return (datetime.now(timezone.utc) - launch_time).days if launch_time else 0

def create_empty_df(columns):
    return pd.DataFrame(columns=columns)

def remove_duplicates(df, column_name):
    """Remove duplicates based on a specific column name."""
    return df.drop_duplicates(subset=[column_name])

# def convert_lists_to_strings(df):
#     """Convert list columns to strings for a given DataFrame."""
#     for col in df.columns:
#         if df[col].apply(lambda x: isinstance(x, list)).any():
#             df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)
#     return df

def convert_lists_to_strings(df):
    """Convert list columns to strings for a given DataFrame."""
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)
    return df

# def save_to_excel(filename, **services):
#     try:
#         # Convert list columns to strings and remove duplicates for all dataframes in services
#         for service_name, df in services.items():
#             if df is not None and not df.empty:
#                 df = convert_lists_to_strings(df)
#                 if service_name == 'ecs':
#                     df = remove_duplicates(df, "Service Name")
#                 services[service_name] = df

#         with pd.ExcelWriter(filename, engine='openpyxl') as writer:
#             for service_name, df in services.items():
#                 if df is not None and not df.empty:
#                     df.to_excel(writer, sheet_name=service_name.upper(), index=False)
#         print(f"Data saved to {filename}")
#     except Exception as e:
#         print(f"Error saving to Excel: {e}")

# def save_to_excel(filename, **services):
#     try:
#         # Filtrar apenas os DataFrames que não são None e não estão vazios
#         non_empty_services = {name: df for name, df in services.items() if df is not None and not df.empty}
        
#         # Identificar serviços que não têm dados
#         empty_services = [name for name, df in services.items() if df is None or df.empty]
        
#         if not non_empty_services:
#             print(f"The resources {', '.join(empty_services)} do not exist. Excel file will not be created.")
#             return

#         with pd.ExcelWriter(filename, engine='openpyxl') as writer:
#             for service_name, df in non_empty_services.items():
#                 df = convert_lists_to_strings(df)
#                 if service_name == 'ecs':
#                     df = remove_duplicates(df, "Service Name")
#                 df.to_excel(writer, sheet_name=service_name.upper(), index=False)
#         print(f"Data saved to {filename}")
#     except Exception as e:
#         print(f"Error saving to Excel: {e}")

def save_to_excel(filename, **services):
    try:
        # Filtrar apenas os DataFrames que não são None e não estão vazios
        non_empty_services = {name: df for name, df in services.items() if df is not None and not df.empty}
        # print(non_empty_services) # Para debug
        # Identificar serviços que não têm dados
        empty_services = [name for name, df in services.items() if df is None or df.empty]

        if not non_empty_services:
            print(f"The resource(s) {', '.join(empty_services)} does not exist. Excel file will not be created/saved.")
            return

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for service_name, df in non_empty_services.items():
                df = convert_lists_to_strings(df)
                if service_name == 'ecs':
                    df = remove_duplicates(df, "Service Name")
                    # Ordenar o DataFrame de acordo com a coluna 1
                    df = df.sort_values(by=df.columns[0], ascending=True)
                df.to_excel(writer, sheet_name=service_name.upper(), index=False)
            # print(df) # Para debug 
            print(f"\nData saved to {filename}")

        # Imprimir mensagem para serviços que não têm dados
        if empty_services:
            print(f"The resource(s) {', '.join(empty_services)} does not exist.")

    except Exception as e:
        print(f"\nError saving to Excel: {e}")

def format_tags(tags):
    """Format tags dictionary into a multi-line string with commas."""
    formatted_tags = [f"{key}: {value}," for key, value in tags.items()]
    if formatted_tags:
        formatted_tags[-1] = formatted_tags[-1].rstrip(',')  # Remove the comma from the last item
    return '\n'.join(formatted_tags)

def format_service_info(service):
    """Format service information from dictionary to key: value pairs."""
    formatted_service = [f"{key}: {value}" for key, value in service.items()]
    return ', '.join(formatted_service)


# def save_account_name_to_excel(filename, account_name):
#     try:
#         df = pd.DataFrame({"Account Name": [account_name]})
#         with pd.ExcelWriter(filename, engine='openpyxl') as writer:
#             df.to_excel(writer, sheet_name='AccountName', index=False)
#         print(f"Account name saved to {filename}")
#     except Exception as e:
#         print(f"Error saving account name to Excel: {e}")