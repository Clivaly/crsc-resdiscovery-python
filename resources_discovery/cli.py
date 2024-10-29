import cmd
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.asg import get_asg_instances
from src.dynamodb import get_dynamodb_tables
from src.ebs import get_ebs_volumes
from src.ec2 import get_ec2_instances
from src.ecs import get_ecs_services
from src.elb import get_load_balancers
from src.glue import get_glue_jobs
from src.kineses import get_kinesis_streams
from src.lambdas import get_lambda_functions
from src.rds import get_rds_aurora_instances, get_rds_instances
from src.utils.utils import save_to_excel

class MyCLI(cmd.Cmd):
    intro = '->> Bem-vindo ao terminal interativo. <<-\n** Digite help ou ? para listar os comandos. **\n'
    prompt = '(cli-$->>) '

    def do_ls(self, arg):
        """List all available services."""
        services = ["EC2", "RDS", "Aurora", "EBS", "Lambda", "DynamoDB", "ASG", "ELB", "Glue", "Kinesis", "ECS"]
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
            "ECS": get_ecs_services
        }
        service_upper = service.upper()
        if service_upper in service_functions:
            return service_upper.lower(), service_functions[service_upper]()
        else:
            raise ValueError(f"Service {service} is not implemented yet.")

    def do_svc(self, arg):
        """Get information for selected services. Usage: svc EC2 RDS"""
        services = arg.split()
        if not services:
            print("No services selected. Use svc <service1> <service2> ... to select services.")
            return

        data_frames = {}
        with ThreadPoolExecutor() as executor:
            future_to_service = {executor.submit(self.fetch_service_data, svc): svc for svc in services}
            for future in as_completed(future_to_service):
                svc = future_to_service[future]
                try:
                    service_name, df = future.result()
                    data_frames[service_name] = df
                except Exception as exc:
                    print(f"Service {svc} generated an exception: {exc}")

        if data_frames:
            save_to_excel('aws_discovery_report.xlsx', **data_frames)

    def do_get_all(self, arg):
        """Get information for all services."""
        services = ["EC2", "RDS", "Aurora", "EBS", "Lambda", "DynamoDB", "ASG", "ELB", "Glue", "Kinesis", "ECS"]
        data_frames = {}
        with ThreadPoolExecutor() as executor:
            future_to_service = {executor.submit(self.fetch_service_data, svc): svc for svc in services}
            for future in as_completed(future_to_service):
                svc = future_to_service[future]
                try:
                    service_name, df = future.result()
                    data_frames[service_name] = df
                except Exception as exc:
                    print(f"Service {svc} generated an exception: {exc}")

        if data_frames:
            save_to_excel('aws_discovery_report.xlsx', **data_frames)

    def do_exit(self, arg):
        """Exit the CLI."""
        print("Exiting...")
        return True

if __name__ == '__main__':
    MyCLI().cmdloop()