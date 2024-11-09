import cmd
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init
from halo import Halo
from src.apigateway import get_api_gateways
from src.asg import get_asg_instances
from src.dynamodb import get_dynamodb_tables
from src.ebs import get_ebs_volumes
from src.ec2 import get_ec2_instances
from src.ecs import get_ecs_services
from src.eks import get_eks_clusters
from src.elb import get_load_balancers
from src.glue import get_glue_jobs
from src.sqs import get_sqs_queues
from src.account import get_account_id
from resources_discovery.src.kinesis import get_kinesis_streams
from src.lambdas import get_lambda_functions
from src.rds import get_rds_aurora_instances, get_rds_instances
from src.utils.utils import save_to_excel
import time

# Inicializa o colorama
init(autoreset=True)

class MyCLI(cmd.Cmd):
    intro = '''
####### Bem-vindo ao terminal interativo. #######
        .--.             .--.
     .-(    ).        .-(    ).
    (___.__)__)      (___.__)__)
    
->> Digite help ou ? para listar os comandos. <<-
'''
    prompt = 'cmd-$ '

    def do_id(self, arg):
        ...
        # """List the AWS account ID."""
        # account_id = get_account_id()
        # print(f"AWS Account ID: {account_id}")

    def do_ls(self, arg):
        """List all available services."""
        services = ["EC2", "RDS", "Aurora", "EBS", "Lambda", "DynamoDB", "ASG", "ELB", "Glue", "Kinesis", "ECS", "EKS", "SQS", "GTW"]
        print("Available services:")
        for service in services:
            print(f"- {service}")

    def fetch_service_data(self, service):
        service_functions = {
            "EC2": get_ec2_instances,
            "RDS": get_rds_instances,
            "AURORA": get_rds_aurora_instances,
            "EBS": get_ebs_volumes,
            "LAMBDA": get_lambda_functions,
            "DYNAMODB": get_dynamodb_tables,
            "ASG": get_asg_instances,
            "ELB": get_load_balancers,
            "GLUE": get_glue_jobs,
            "KINESIS": get_kinesis_streams,
            "ECS": get_ecs_services,
            "EKS": get_eks_clusters,
            "SQS": get_sqs_queues,
            "GTW": get_api_gateways
        }
        service_upper = service.upper()
        if service_upper in service_functions:
            return service_upper.lower(), service_functions[service_upper]()
        else:
            raise ValueError(f"Service {service} is not implemented yet.")

    def do_get(self, arg):
        """Get information for selected services. Usage: get EC2 RDS"""
        services = arg.split()
        if not services:
            print("No services selected. Use get <service1> <service2> ... to select services.")
            return

        data_frames = {}
        successful_services = []
        failed_services = []
        start_time = time.time()
        with ThreadPoolExecutor() as executor:
            future_to_service = {executor.submit(self.fetch_service_data, svc): svc for svc in services}
            total = len(future_to_service)
            current = 0
            with Halo(text='Listando dados', spinner='dots1') as spinner:
                for future in as_completed(future_to_service):
                    svc = future_to_service[future]
                    try:
                        service_name, df = future.result()
                        data_frames[service_name] = df
                        successful_services.append(svc)
                    except Exception as exc:
                        print(f"Service {svc} generated an exception: {exc}")
                        failed_services.append(svc)
                    current += 1
                    spinner.text = f"Fetching data: {current}/{total}"

        if data_frames:
            save_to_excel('aws_discovery_report.xlsx', **data_frames)

        # Display summary
        print("\nSummary:")
        if successful_services:
            print(Fore.GREEN + "Successfully fetched data for:")
            for svc in successful_services:
                print(f"- {svc}")
        if failed_services:
            print(Fore.RED + "Failed to fetch data for:")
            for svc in failed_services:
                print(f"- {svc}")

    def do_get_all(self, arg):
        """Get information for all services."""
        services = ["EC2", "RDS", "Aurora", "EBS", "Lambda", "DynamoDB", "ASG", "ELB", "Glue", "Kinesis", "ECS", "EKS", "SQS", "GTW"]
        data_frames = {}
        successful_services = []
        failed_services = []
        start_time = time.time()
        with ThreadPoolExecutor() as executor:
            future_to_service = {executor.submit(self.fetch_service_data, svc): svc for svc in services}
            total = len(future_to_service)
            current = 0
            with Halo(text='Fetching data', spinner='dots') as spinner:
                for future in as_completed(future_to_service):
                    svc = future_to_service[future]
                    try:
                        service_name, df = future.result()
                        data_frames[service_name] = df
                        successful_services.append(svc)
                    except Exception as exc:
                        print(f"Service {svc} generated an exception: {exc}")
                        failed_services.append(svc)
                    current += 1
                    spinner.text = f"Fetching data: {current}/{total}"

        if data_frames:
            save_to_excel('aws_discovery_report.xlsx', **data_frames)

        # Display summary
        print("\nSummary:")
        if successful_services:
            print(Fore.GREEN + "Successfully fetched data for:")
            for svc in successful_services:
                print(f"- {svc}")
        if failed_services:
            print(Fore.RED + "Failed to fetch data for:")
            for svc in failed_services:
                print(f"- {svc}")

    def do_exit(self, arg):
        """Exit the CLI."""
        print("Exiting...")
        return True

if __name__ == '__main__':
    MyCLI().cmdloop()