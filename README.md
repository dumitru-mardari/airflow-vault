# Apache Airflow ETL with HashiCorp Vault integration
This is my project that integrates HashiCorp Vault as secrets-backend for Apache Airflow 2.7.2. The secrets (e.g., AWS connections, variables) are stored in the HashiCorp Vault secrets-manager. AWS Connections are used for connection to AWS Cloud for the purpose of sensing new files (.csv) being uploaded to S3 Bucket repositories, and for retrieval of those files from S3 Buckets for further data pre-processing. The processed data is then loaded into MongoDB NoSQL database and PostgreSQL Database. Both - Apache Airflow and HashiCorp Vault - are deployed using Docker Compose. The steps to replicate this project are described below.
![Image Alt Text](https://raw.githubusercontent.com/dumitru-mardari/airflow-vault/main/images/workflow.png)
## Contents
Part | Title
-|-
1| Environment setup 
2| Configuring HashiCorp Vault deployment using Docker 
3| Configuring Apache Airflow 
4| Create Extract, Transform and Load task using DAGs
5| Options for improvements
6| Remarks

## 1. Environment setup
- Virtual machine - Linux x86_64 Architecture - Linux Mint 21.2 Distribution
- Allocated RAM 16 GB, 4 Processors x 2 Cores = 8 Total Cores, 120 GB SSD, GPU 8GB, Network connection: NAT
- Installed Docker Compose v2.22.0
- Installed Docker Desktop v4.24.0 (122432). CPU limit: 8 cores; Memory Limit: 4.5 GB, Swap: 1 GB
- Installed Python 3.10.12

## 2. Configuring HashiCorp Vault deployment using Docker
1. Create a Vault project directory - `/vault`.
```
$ mkdir vault
```
\
2. Create `docker-compose.yml` file, `/config` and `/file` directories inside the `/vault` project directory.
```
$ cd vault
/vault$ touch docker-compose.yml
/vault$ mkdir config file
```
\
3. Enter `/config` directory and create `vault.hcl` file (configuration file for HashiCorp Vault).
```
/vault$ cd config
/vault$ touch vault.hcl
```
\
4. Replace the contents of Vault's `docker-compose.yml` and `vault.hcl` with the ones from this repository.  
\
5. Make sure that the `/vault` dir is having proper permissions and ownership. You must have full read and write access to all files in `/vault` dir, and have ownership over them. Right click `/vault` dir and check Properties>Permissions. If these are not correct, you can change them using the following commands:
```
# This will change ownership of your /vault dir and all files within recursively to user: <your-username>, group: <your-username>
/projects$ chown <your-username>:<your-username> -R vault
# This will change permissions for users and groups to read, write, access your /vault dir and all files within recursively
/projects$ chmod -R +rwx vault && chmod -R g+rwx vault
```
\
6. From `/vault` directory, run docker compose command to deploy Vault's docker container. This will deploy the container for latest HashiCorp Vault Docker image available in Docker Hub. All the outputs of deployment will be shown in the terminal. Do not press CTRL+C. This will interrupt the deployment of container.
```
/vault$ docker compose up
```
\
7. After a while, Vault UI should be accessible in browser at: http://localhost:8200 . Access it.  
\
8. Set number of "Key shares" and "Key threshold" to your preference (e.g., 1 and 1). Initialize it.  
\
9. IMPORTANT! Copy your "Initial root token" and "Key 1 + any other keys" to a safe place. You can optionally download keys or save them to your host environment variables.
```
$ export VAULT_TOKEN=<token>
$ export VAILT_UNSEAL_KEY1=<key1>
```
\
10. Continue to unseal the vault by providing the "Unseal Key Portion".  
\
11. Login to your vault using the initial root token (token of your vault's root user).  
\
12. You might want to have access to vault using username/password combination, instead of token. For this, go to "Access" in the left pane in Vault's UI and click "Enable new method +" on the right side. Choose "Username & Password" option. We will also need it later for setting up a user for Apache Airflow. Click Next, "Enable Method" and "Update Options".  
\
13. Click the newly appeared "userpass/" authentication method and "Create user +" from the window's right side. Insert username `root` and password `<your-password-of-choice>`, and click "Save".  
\
14. Create another user for Apache Airflow using the same procedure. Username `airflow` and pass `airflow2023!` will be used in further steps.  
\
15. Now, we want to create new policies for our root and airflow users. Get back to main menu and click "Policies". Click "Create ACL Policy". For root user, name the policy `root-policy` and provide the following JSON code for the policy:
```
path "*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}
```
\
16. For your airflow user, create a policy named `airflow` with the following code. This will allow airflow user to access only the `airflow` secrets-engine and all secrets stored within it.
```
airflow:
path "airflow/*" {
  capabilities = ["read"]
}
```
\
17. We now need to assign the policies to respective users. For this, you can use the terminal available in the menu. 
```
# Assign policy for root user
vault write auth/userpass/users/root/policies policies="root-policy"
# Assign policy for airflow user
vault write auth/userpass/users/airflow/policies policies="airflow"
```
\
18. Now, we need to create the `airflow` secrets engine where we can store our secret connections (e.g., AWS Keys and Secret Keys) and variables. Click on "Secrets engines" from the left pane and "Enable new engine +". Select `KV` engine and click Next. Define `airflow` as Path and click Next.  
\
19. Now, we can put our first connections and variables. For this purpose, we will insert a `smtp_default` secret connection, an AWS Key pair `aws_conn` connection and a `test_var` variable. Now, click on "Create secret +". For "Path of this secret", type `connections/aws_conn`. In "Secret data", type the following:
```
# Key - variable. Add new keys for login and password.
conn_type - aws
login - <your AWS KEY>
password - <your AWS SECRET KEY
```
\
20. Create an `smtp_default` secret connection on `connections/smtp_default` path using the same procedure. You can use it later for test purposes.
```
conn_type - smtps
host - relay.example.com
login - user
password - host
port - 465
```
\
21. Add a secret variable in `airflow` secrets engine. Again, using the same procedure, click on "Create Secret +", provide path `variables/test_var` and the secret pair:
```
# Key - variable
key - test123
```
\
FYI 1: You can shut down Vault's container by entering Docker Desktop and stopping by the container. Starting it again will load any new changes made to the configuration file.
FYI 2: By default, every time you switch off the Vault container, the Vault gets sealed. You need the `KEY 1` and, if applicable, any additional keys, to unseal the vault at every container startup. You can create your own docker compose to add an additional container that will unseal the Vault at startup using the provided keys. However, this is out of scope for this project.  
\
Now, you've completed configuring your HashiCorp Vault instance. In the next step, we will start configuring Apache Airflow to securely retrieve secrets from the Vault.  
  
## 3. Configuring Apache Airflow

1. In your projects directory, create a new directory for Apache Airflow.
```
/projects$ mkdir apache-airflow
```
\
2. Create several new dirs in `/apache-airflow`. These dirs will be used for mapping to the respective dirs within the Apache Airflow container. `/config` is used for storing config files. `/dags` is used for storing DAGs. `/data` is used as backend storage. `/logs` is used for storing logs. `/plugins` is used for storing plugins.
```
$ cd apache-airflow
/apache-airflow$ mkdir config dags data logs plugins
```
\
3. Fetch the `docker-compose.yaml` file from official website.
```
/apache-airflow$ curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.7.2/docker-compose.yaml'
```
\
4. Fetch the `airflow.sh` file from official website. It can be used for running airflow commands.
```
/apache-airflow$ curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.7.2/airflow.sh'
# You can used it later, when the airflow container will be up, to run airflow commands like "airflow info":
/apache-airflow$ ./airflow.sh info 
```
\
5. Move to `/config` and create `airflow.cfg` and `webserver_config.py`.
```
# airflow.cfg - stores any configuration parameters
# webserver_config.py - stores any airflow-webserver configuration parameters
/apache-airflow/config$ touch airflow.cfg webserver_config.py
```
\
6. Create a backup files for `airflow.cfg` and `docker-compose.yaml`:
```
/apache-airflow/config$ cd ..
/apache-airflow$ cp config/airflow.cfg config/airflow.cfg.bak
/apache-airflow$ cp docker-compose.yaml docker-compose.yaml.bak
```
\
7. Fill the contents of `airflow.cfg` and `docker-compose.yaml` with the contents from the respective files available in this repository OR make the necessary changes as described below.  
\
Now, we need to make some changes in parameters within `airflow.cfg` . I suggest you read the parameters and their descriptions in your free time to configure airflow to your liking.  
\
FYI: You can also parse parameters to `docker-compose.yaml` under common or service-specific environment variables. To define attibutes in `docker-compose.yaml` , use the pattern {AIRFLOW}{DOUBLE_UNDERSCORE}{SERVICE}{DOUBLE_UNDERSCORE}{PARAMETER}, e.g., `AIRFLOW__CORE__LOAD_EXAMPLES` . However, the parameter values defined in `airflow.cfg` will take precedence, aka have higher priority, over the parameters defined in `docker-compose.yaml` .  
\
8. Under `[webserver]`, change `default_timezone` to your timezone (e.g., UTC+1).  
\
9. Under `[webserver]`, change `default_ui_timezone` to your timezone.  
\
10. Under `[webserver]`, add `rbac = true` to enable Role-Based Access Control security feature.  
\
11. Under `[scheduler]`, change `parallelism = 4` to limit concurrent amount of DAG tasks being run. We don't need more than 4 at this time. You can change back to default number later.  
\
12. Under `[scheduler]`, change `dag_dir_list_interval = 30` to change the time interval the scheduler scans `/dag` directory for new dags. 300sec is good for production, but not for development.  
\
13. Under `[core]`, change `max_active_tasks_per_dag = 4` to limit maximum active tasks per DAG. We don't need more than 4 at this time. You can change back to default number later.  
\
14. Under `[core]`, change `max_active_runs_per_dag = 4` to limit maximum concurent runs of one DAG. We don't need more than 4 at this time. You can change back to default number later.  
\
15. Under `[core]`, change `load_examples = False` to disable load of "example" DAGs on startup. We don't need example DAGs.  
\
16. Under `[secrets]`, change `backend = airflow.providers.hashicorp.secrets.vault.VaultBackend` to enable Vault as secrets backend.  
\
17. Under `[secrets]`, change `backend_kwargs = {"auth_type":"userpass","username":"airflow","password":"airflow2023!","mount_point": "airflow","connections_path":"connections","variables_path": "variables","url": "http://172.26.0.2:8200"}` . We will authenticate to Vault using userpass method. You can consult HashiCorp docs for additional authentication methods and how to set them up: https://developer.hashicorp.com/vault/docs/auth . For userpass authetication method, we will use the credentials that we've created earlier. The mount point refers to the secrets engine. URL refers to the Vault's IP address and port for retrieval of secrets using API. To find your your Vault's container IP address, you can open Docker Desktop>Select Vault container that uses the hashicorp/vault:latest image>Inspect>Networks>"IPAddgress".  
\
18. Under `[celery]`, change `worker_concurrency = 4` to define the amount of tasks a celery worker can take. For development purpose, we don't need more than 4.  
\
19. After you have inserted content from this repository to your `airflow.cfg`, `webserver_config.py` and `docker-compose.yaml` OR you have made necessary parameter value changes, you can now deploy your airflow multi-container.
```
/apache-airflow$ docker compose up
```
\
The Airflow UI should be accessible at: http://localhost:8080/ . Login using default credentials username: `airflow` and password: `airflow` .  
\
FYI 1: For troubleshooting purposes, you can disable the mounting of `airflow.cfg` and `webserver_config.py` in `docker-compose.yaml` by commenting them out with `#` . You can then deploy the airflow multi-container from `/apache-airflow$` dir using `docker compose up` command and inspect the default versions of those files within the `airflow-webserver` container, using Docker Desktop. If `aiflow.cfg` wasn't mounted as a volume in `docker-compose.yaml`, the container will create its own `airflow.cfg` with default parameter values. The `airflow.cfg` is located in `<airflow-webserver-container>/opt/airflow/airflow.cfg` . You can navigate to this path using Docker Desktop and download these files in original configuration.  
\
Now, we've setup the Airflow service and we're ready to create the necessary DAGs for the ETL workflow (Extract data from S3, Transform data using Python, Load data into Amazon Redshift DWH).  

## 4. Create Extract, Transform and Load task using DAGs

In this chapter, we create the DAG for defining the ETL workflow described above.

The necessary imports are described below:
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
# Vault connections
from airflow.hooks.base_hook import BaseHook
# S3 file sensing and download
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
# PostgreSQL
import psycopg2
from airflow.operators.postgres_operator import PostgresOperator
from sqlalchemy import create_engine
# MongoDB
from airflow.providers.mongo.hooks.mongo import MongoHook
```
\
The DAGs must be placed in `/apache-airflow/dags` dir. New DAGs will be picked by airflow-scheduler within a 30sec time interval, as defined in `airflow.cfg`. When retrieving secrets from Vault using Airflow, the secrets are encrypted at runtime and cannot be printed out for inspection (except for public keys). Therefore, you might wish to modify your Airflow policies to restrict access to logs and connections for specific users. Since it is possible to retrieve and store secrets at runtime (not in the scope of this project), users can then navigate the Airflow UI>Admin>Connections in order to inspect the KEYS and SECRET KEYS.
\
![Image Alt Text](https://raw.githubusercontent.com/dumitru-mardari/airflow-vault/main/images/workflow.png)\
\
The DAG that defines the ETL workflow for this project is stored in `/apache-airflow/dags` .

1. `t1_test_sensor` Continous sensor for sensing a file withing an S3 Bucket. Task is marked as "success" as soon as file is found, otherwise "running'.
2. `t2_test_download` Task to download the file to the backend storage of Airflow `/apache-airflow/data`.
3. `t3_rename_file` Task to rename downloaded file since Airflow downloads the file and names it arbitrarily.
4. `t4_split` Task to split file (.csv) into multiple parts. In our case, the task splits "test" dataset used for fitting ML models. The dataset needs to be split into 5 equal smaller datasets.
5. `t5_tests_to_json` MongoDB requires data to be uploaded in BSON formatted JSON files. This task transforms Pandas dataframes into BSON formatted data and stores it locally in Airflow storage.
6. `t6_1_upload_mongo` Upload of JSON files to MongoDB.
7. `t6_2_1_create_tables` This step is optional. Here, tables are created in PostgreSQL before data is uploaded to the database. If tables exist already in the database, any records in those tables will be wiped before new data will be uploaded.
8. `t6_2_2_load_data` Upload of data to PostgreSQL.

## 5. Options for improvement
- Parse the data between DAG tasks using XCOM instead of saving data locally.
- [Optional] Define all containers (PostgreSQL, MongoDB, etc.) inside one docker-compose multi-container.

## 6. Remarks
- The main network is defined in the Vault container since it is the most persistent micro-service.

