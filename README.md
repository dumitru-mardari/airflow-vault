# Apache Airflow with HashiCorp Vault integration
This is my project that integrates HashiCorp Vault as secrets-backend for Apache Airflow 2.7.2. The secrets (e.g., AWS connections, variables) are stored in the HashiCorp Vault secrets-manager. AWS Connections are used for connection to AWS Cloud for the purpose of sensing new files (.csv) being uploaded to S3 Bucket repositories, and for retrieval of those files from S3 Buckets for further data pre-processing. Both - Apache Airflow and HashiCorp Vault - are deployed using Docker Compose files.  

## Contents
| Part | Title |
|-|-|
|   1  | Setup environment |
|   2  | Configuring HashiCorp Vault |
|   3  | Configuring Apache Airflow |
|   4  | References |


## Setup environment
- Virtual machine - Linux - Linux Mint 21.2 Distribution
- RAM 16 GB, 4 Processors x 2 Cores = 8 Total Cores, 120 GB SSD (80 GB not enough), GPU 8GB, Network connection: NAT
- Installed Docker Compose v2.22.0
- Installed Docker Desktop v4.24.0 (122432). CPU limit: 8 Cores, Memory Limit: 4.5 GB, Swap: 1 GB
- Installed Python 3.10.12 (`python3 --version`)

## Configuring HashiCorp Vault
1. Create your directory for HashiCorp Vault.
```
mkdir vault
```
3. 
## Configuring Apache Airflow
```

```

`code`

## References
