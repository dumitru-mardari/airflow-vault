# Apache Airflow with HashiCorp Vault integration
This is my project that integrates HashiCorp Vault as secrets-backend for Apache Airflow 2.7.2.
The secrets (e.g., AWS connections, variables) are stored in the HashiCorp Vault secrets-manager.
The secret AWS Connections are used for connection to AWS Cloud for the purpose of sensing new files (.csv) being uploaded to S3 Bucket repositories, and for retrieval of those files from S3 Buckets for further data pre-processing.
Both - Apache Airflow and HashiCorp Vault - are deployed using Docker Compose files.

## Contents
| Part | Title |
|-|-|
|  1  | Setup |
|  2  | Configuring Docker Desktop |
|  3  | Configuring HashiCorp Vault |
|  4  | Configuring Apache Airflow |
|  5  | References |


## Setup
- Virtual machine - Linux - Linux Mint 21.2 Distribution
- RAM 16 GB, 4 Processors x 2 Cores = 8 Total Cores, 120 GB SSD (80 GB not enough), Network connection: NAT
- Installed Docker Compose v2.22.0
- Installed Docker Desktop v4.24.0 (122432)
- Installed Python 3.10.12 (check command: python3 --version)

## Configuring Docker Desktop
- CPU limit: 8, Memory Limit: 4.5 GB, Swap: 1 GB

## Configuring HashiCorp Vault

## Configuring Apache Airflow
```

```

`code`

## References
