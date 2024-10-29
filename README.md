# CRSC Resources Discovery

## Visão Geral

O CRSC Resources Discovery é uma ferramenta de descoberta de recursos da nuvem AWS desenvolvida em Python. Ela permite que você descubra e gerencie recursos da AWS de forma eficiente e escalável.

## Objetivos

* Descobrir recursos da AWS, incluindo EC2, RDS, Aurora, EBS, ASG, ELB, Glue, Kinesis, ECS, Lambda e DynamoDB
* Salvar informações dos recursos em uma planilha do Excel para fácil análise e gerenciamento
* Fornecer uma interação via cli intuitiva e fácil de usar

## Resumo

Este projeto é uma implementação em Python de um sistema de descoberta de serviços da nuvem AWS. Ele utiliza a AWS CLI para interagir com a conta AWS e descobrir informações sobre os seguintes serviços:

* EC2
* RDS && Aurora
* EBS
* ASG
* ELB
* Glue
* Kinesis
* ECS
* Lambda
* DynamoDB

## Requisitos

* Python >= 3.11.
* Poetry para gerenciamento de dependências.
* Bibliotecas necessárias:
  + `boto3` para interagir com a AWS.
  + `pandas` para salvar as informações em uma planilha do Excel.
* AWS CLI configurado com acesso à conta AWS.

## Instalação

1. Clone o repositório: `git clone https://github.com/Clivaly/crsc-resdiscovery-python.git`.
2. Instale as dependências com Poetry: `poetry install`.
3. Configure o AWS CLI com acesso à conta AWS.

## Uso

1. Execute o comando principal: 
```sh
poetry run python ./resources_discovery/main.py