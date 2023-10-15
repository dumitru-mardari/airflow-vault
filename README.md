# ATTENTION! CURRENTLY IN DEVELOPMENT! DO NOT REPRODUCE STEPS!

# Tutorial: Apache Airflow with HashiCorp Vault integration
This is my project that integrates HashiCorp Vault as secrets-backend for Apache Airflow 2.7.2. The secrets (e.g., AWS connections, variables) are stored in the HashiCorp Vault secrets-manager. AWS Connections are used for connection to AWS Cloud for the purpose of sensing new files (.csv) being uploaded to S3 Bucket repositories, and for retrieval of those files from S3 Buckets for further data pre-processing. Both - Apache Airflow and HashiCorp Vault - are deployed using Docker Compose files.  

## Contents
| Part | Title |
|-|-|
|   1  | Setup environment |
|   2  | Configuring HashiCorp Vault deployment using Docker |
|   3  | Configuring Apache Airflow |
|   4  | References |


## Setup environment
- Virtual machine - Linux - Linux Mint 21.2 Distribution
- RAM 16 GB, 4 Processors x 2 Cores = 8 Total Cores, 120 GB SSD (80 GB not enough), GPU 8GB, Network connection: NAT
- Installed Docker Compose v2.22.0
- Installed Docker Desktop v4.24.0 (122432). CPU limit: 8 Cores, Memory Limit: 4.5 GB, Swap: 1 GB
- Installed Python 3.10.12 (`python3 --version`)

## Configuring HashiCorp Vault deployment using Docker
1. Create a Vault project directory - "vault".
```
$ mkdir vault
```
2. Create "docker-compose.yml" file, "config" and "file" directories inside the /vault project directory.
```
$ cd vault
/vault$ touch docker-compose.yml
/vault$ mkdir config file
```
3. Enter /config directory and create "vault.hcl" file (configuration file for HashiCorp Vault).
```
/vault$ cd config
/vault$ touch vault.hcl
```
4. Replace the contents of Vault's docker-compose.yml and vault.hcl with the ones from this repository.
5. From vault directory, run docker compose command to deploy Vault's docker container. This will deploy the container for latest HashiCorp Vault Docker image available in Docker Hub. All the outputs of deployment will be shown in the terminal. Do not press CTRL+C. This will interrupt the deployment of container.
```
/vault$ docker compose up
```
6. Vault UI should be accessible in browser at: http://localhost:8200
7. 

## Configuring Apache Airflow
```

```

`code`

## References
