# CRSC Resources Discovery

## Visão Geral 
Esta ferramenta de linha de comando (CLI) em Python coleta informações sobre vários recursos da AWS e salva os dados em um arquivo Excel.
 
## Índice
 
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Funcionalidades](#funcionalidades)
- [Estrutura do Código](#estrutura-do-código)
- [Erros Comuns](#erros-comuns)
<!-- - [Contribuição](#contribuição) -->
- [Licença](#licença)
 
## Pré-requisitos
 
- AWS CLI configurado com as credenciais apropriadas:
```sh
    aws configure
```
- Certifique-se de ter as seguintes bibliotecas Python instaladas:
```sh
    pip install boto3 pandas openpyxl halo
```
- ou, se preferir, utilize o Poetry:
```sh
poetry add boto3 pandas openpyxl halo
```
## Instalação
- Clone o repositório:
```sh
    git clone https://github.com/seu-usuario/aws-resources-report.git
```
cd aws-resources-report
- Instale as dependências usando o Poetry:
```sh
    poetry install
```
- Ative o ambiente virtual:
```sh
    poetry shell
```
 
## Uso
- Para iniciar o programa, execute o comando:
```sh
    poetry run python ./discovery_report/main.py
```
#### Comandos Disponíveis:
- **ls** -> Listar serviços disponíveis
- **get_all** -> Obter informações de todos os serviços
- **get <serviço1> <serviço2>** ->  Obter informações de serviços específicos, exemplos: listar único servico: **get ec2**, listar um ou mais serviços: **get eks rds glue**
 
## Funcionalidades
Coleta de Dados de Recursos AWS: EC2, RDS, EBS, Lambda, DynamoDB, ASG, Load Balancers, Glue, Kinesis, ECS, EKS, SQS.
Formatação de Data: Converte strings de data para o formato dia-mês-ano.
Verificação de Expiração de AMI: Verifica se uma AMI está expirada.
Verificação de Estado Ocioso: Calcula o número de dias que uma instância ou volume está ocioso.
Salvamento em Excel: Salva os dados coletados em um arquivo Excel.
 
## Estrutura do Código
O código está organizado em módulos, cada um responsável por interagir com um serviço AWS específico. A CLI orquestra a execução dos comandos e a coleta de dados.
 
## Erros Comuns
- Credenciais Inválidas: Verifique suas credenciais AWS.
- Permissões Insuficientes: Verifique as permissões do usuário IAM.
- Dependências Faltando: Certifique-se de que todas as bibliotecas necessárias estão instaladas.
 
<!-- ## Contribuição
Sinta-se à vontade para contribuir com melhorias. Faça um fork do repositório, crie uma branch para suas alterações e envie um pull request. -->
 
## Licença
Este projeto está licenciado sob os termos da licença Apache2.