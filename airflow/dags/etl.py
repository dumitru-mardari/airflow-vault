from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base_hook import BaseHook
from datetime import datetime, timedelta
# S3
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
# PostgreSQL
from airflow.operators.postgres_operator import PostgresOperator

# DAG
default_args = {
    'owner' : 'airflow',
    'start_date' : datetime(2023, 10, 20),
    'retries': '1',
    'schedule_interval' : 'None',
    'catchup': 'False',
    'dagrun_timeot': 'None',
    }

dag =  DAG(
    'houseprices-dataset-2',
    default_args = default_args,
    description = 'ETL S3'
    )

# Task 1 - Test sensor in S3
# Get aws_conn connection from Vault
BaseHook.get_connection('aws_conn')

t1_test_sensor = S3KeySensor(
    aws_conn_id='aws_conn',
    task_id='t1_test_sensor',
    bucket_key='test.csv',
    bucket_name='khouseprices',
    dag=dag,
)

# Task 2 - Test download from S3
def download_from_s3(conn: str,key: str, bucket_name:str, local_path: str) -> str:
    return S3Hook(conn).download_file(
        key = key,
        bucket_name = bucket_name,
        local_path = local_path,
        )

t2_test_download = PythonOperator(
    task_id = 't2_test_download',
    python_callable = download_from_s3,
    op_kwargs = {
        'conn': 'aws_conn',
        'key': 'test.csv',
        'bucket_name': 'khouseprices',
        'local_path': '/opt/airflow/data/',
        },
    dag = dag,
    )

# Task 3 - Rename Test
def rename_file(ti, new_name: str) -> None:
    import os
    download_file_name = ti.xcom_pull(task_ids = ['t2_test_download'])
    downloaded_file_path = '/'.join(download_file_name[0].split('/')[:-1])
    os.rename(src = download_file_name[0], dst = f"{downloaded_file_path}/{new_name}")

t3_rename_file = PythonOperator(
    task_id = 't3_rename_file',
    python_callable = rename_file,
    op_kwargs = {
        'new_name': 'testv2.csv'
        },
    dag = dag,
    )

# Task 4 - split data
def split_test():
    import pandas as pd
    import numpy as np
    
    df = pd.read_csv('/opt/airflow/data/testv2.csv', index_col=0)
    
    # Shuffling df
    df = df.sample(frac=1)
    
    # Splitting df into 5 parts
    df = np.array_split(df, 5)

    for i, part_df in enumerate(df):
        part_df.to_csv(f'/opt/airflow/data/testv2{i+1}.csv')

t4_split = PythonOperator(
    task_id = 't4_split',
    python_callable=split_test,
    dag=dag,
)

# Task 5 - tranform csv to json
def convert_cell(cell):
    if cell.isdigit():
        return int(cell)
    try:
        float_val = float(cell)
        if float_val.is_integer():
            return int(float_val)
        return float_val
    except ValueError:
        return cell

# Transform CSV to MongoDB format
def csv_to_mdb(csv_file_path, header = True):
    import csv
    data = {}
    with open (csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        if header:
            header_row = next(csv_reader)
        for row in csv_reader:
            document = dict(zip(header_row, row)) if header else dict(zip([f'field_{i+1}' for i in range(len(row))], row))
            key = row[0] if row else None
            if key:
                data[key] = document
    return data

# Save MDB-formatted file as JSON
def save_file(data, output_json_file):
    import json
    with open(output_json_file, 'w') as json_file:
        json.dump(data, json_file, indent=2)

def tests_to_json():
    import json
    for i in range(5):
        save_file(csv_to_mdb(f'/opt/airflow/data/testv2{i+1}.csv'), f'/opt/airflow/data/testv2{i+1}.json')

t5_tests_to_json = PythonOperator(
    task_id = 't5_tests_to_json',
    python_callable = tests_to_json,
    dag = dag
)

# Task 6_1 - load into MongoDB
def uploadtomongo():
    import json
    from airflow.providers.mongo.hooks.mongo import MongoHook

    BaseHook.get_connection('mongo')

    # Load JSON files into a dict
    data_dict = {}
    for i in range(5):
        data_dict[f'data{i+1}'] = open(f'/opt/airflow/data/testv2{i+1}.json', 'r').read()

    # Connection to MongoDB
    hook = MongoHook(conn_id='mongo')
    client = hook.get_conn()
    # Upload to database admin
    db = client.admin
    # Upload to collection test_col
    collection=db.test_col
    print(f"Connected to MongoDB - {client.server_info()}")
    for i in range(5):
        d = json.loads(data_dict[f'data{i+1}'])
        collection.insert_one(d)

t6_1_upload_mongo = PythonOperator(
    task_id='t6-1_upload_mongo',
    python_callable=uploadtomongo,
    dag=dag
    )

# Task 6_2_1 - create tables in PostgreSQL
def create_tables():
    import psycopg2
    import pandas as pd
    
    postgre_conn = BaseHook.get_connection('postgre')

    # Need 100 rows to assign data type to columns (otherwise wrong data type is assigned) and set index to column 0
    df = pd.read_csv(f'/opt/airflow/data/test.csv', index_col=0)

    id = df.index.name
    
    # Translating Pandas data types to SQL
    mapping = {
        'int64': 'INTEGER',
        'float64': 'FLOAT',
        'object': 'VARCHAR',
    }
    column_types = {column: mapping[str(df[column].dtype)] for column in df.columns}
    
    # Creating SQL strings, e.g., column_name VARCHAR
    column_string = ''
    for i in column_types:
        column_string += f'"{i}" {column_types[i]},\n'
    column_string = column_string.rstrip(',\n')

    # Creating tables in PostgreSQL
    try:
        with psycopg2.connect(
            host = postgre_conn.host,
            dbname = postgre_conn.schema,
            user = postgre_conn.login,
            password = postgre_conn.password,
            port = postgre_conn.port) as conn:
                with conn.cursor() as cur:
            
                    # CREATE TABLE script
                    create_script = f''' 
                    DO $$ 
                    DECLARE
                        i INT := 1;
                    BEGIN
                        WHILE i <= 5 LOOP
                            EXECUTE 'CREATE TABLE IF NOT EXISTS testv2'||i||' (
                                "{id}" SERIAL PRIMARY KEY, 
                                {column_string});';
                            i := i + 1;
                        END LOOP;
                    END $$;
                    '''
                    cur.execute(create_script)
                    print('Tables successfully created!')
    # Error catch
    except Exception as error:
        print(error)
    finally:
        # Closes database connection
        if conn is not None:
            conn.close()

t6_2_1_create_tables = PythonOperator(
    task_id = 't6_2_1_create_tables',
    python_callable = create_tables,
    dag=dag,
)

# Task 6_2_2 - load data
def uploadtopostgre():
    import psycopg2
    import pandas as pd
    from sqlalchemy import create_engine
    
    pg_conn = BaseHook.get_connection('postgre')

    db_params = {
        'database': pg_conn.schema,
        'user': pg_conn.login,
        'password': pg_conn.password,
        'host': pg_conn.host,
        'port': pg_conn.port,
    }

    engine = create_engine(f'postgresql+psycopg2://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}')

    # Clearing tables before data upload
    connection = engine.connect()
    delete_records = [connection.execute(f'DELETE FROM testv2{i+1}') for i in range(5)]
    connection.close()
    
    # Loading dataframes, each into its own table testv2{x} in PostgreSQL
    data_files = [f'/opt/airflow/data/testv2{i+1}.csv' for i in range(5)]
    data_frames = {f'df{i+1}': pd.read_csv(file, index_col=0) for i, file in enumerate(data_files)}
    print('look:' + str(data_frames['df1']['BsmtQual'].dtype))
    data_frames_sql = {f'df{i+1}': df.to_sql(name=f'testv2{i+1}', con=engine, if_exists='append', index=True) for i, df in enumerate(data_frames.values())}

    engine.dispose()

t6_2_2_load_data = PythonOperator(
    task_id = 't6_2_2_load_data',
    python_callable = uploadtopostgre,
    dag=dag,
)

t1_test_sensor >> t2_test_download >> t3_rename_file >> t4_split >> t5_tests_to_json >> [t6_1_upload_mongo, t6_2_1_create_tables]
t6_2_1_create_tables >> t6_2_2_load_data