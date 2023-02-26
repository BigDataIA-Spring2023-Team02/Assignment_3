import os
import time
import boto3
import sqlite3
import pandas as pd
from airflow import DAG
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param

# Set parameters for user input
user_input = {
        "user_sleep_timer": Param(30, type='integer', minimum=10, maximum=120),
        }

# Create DAG with the given parameters
dag = DAG(
    dag_id="Metadata_Airflow",
    schedule="0 5 * * *",   # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["demo_test", "airflow"],
    params=user_input,
)

#set path for env variables
dotenv_path = Path('./.env')

#load env variables
load_dotenv(dotenv_path)

# Set up AWS S3 client with credentials from environment variables
s3client = boto3.client('s3',
                    region_name='us-east-1',
                    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                    )

# Set up AWS CloudWatch logs client with credentials from environment variables
clientLogs = boto3.client('logs',
                region_name='us-east-1',
                aws_access_key_id = os.environ.get('AWS_LOGS_ACCESS_KEY'),
                aws_secret_access_key = os.environ.get('AWS_LOGS_SECRET_KEY')
                )

# Define a function to write logs to AWS CloudWatch
def write_logs(message: str):
    clientLogs.put_log_events(
        logGroupName = "Assignment02-logs",
        logStreamName = "Airflow-Logs",
        logEvents = [
            {
                'timestamp' : int(time.time() * 1e3),
                'message' : message
            }
        ]
    )

# Function to scrape GEOS18 metadata from AWS S3 and store in SQLite database
def scrape_geos18_metadata():
    geos_bucket_name = "noaa-goes18"
    geos18_data_dict = {'ID': [], 'Product_Name': [], 'Year': [], 'Day': [], 'Hour': []}
    
    # Call function to write logs
    write_logs(f"Scraping GEOS18 Metadata into Database")

    id = 1
    prefix = "ABI-L1b-RadC/"
    result = s3client.list_objects(Bucket = geos_bucket_name, Prefix = prefix, Delimiter = '/')
    write_logs(f"Returning list of objects in GEOS18 Bucket for selected prefix {prefix}: {result}")

    # Loop through each object in the result object and get metadata
    for i in result.get('CommonPrefixes'):
        path = i.get('Prefix').split('/')
        prefix_2 = prefix + path[-2] + "/"
        sub_folder = s3client.list_objects(Bucket = geos_bucket_name, Prefix = prefix_2, Delimiter = '/')
        
        for j in sub_folder.get('CommonPrefixes'):
            sub_path = j.get('Prefix').split('/')
            prefix_3 = prefix_2 + sub_path[-2] + "/"
            sub_sub_folder = s3client.list_objects(Bucket = geos_bucket_name, Prefix = prefix_3, Delimiter = '/')
            
            for k in sub_sub_folder.get('CommonPrefixes'):
                sub_sub_path = k.get('Prefix').split('/')
                sub_sub_path = sub_sub_path[:-1]
                geos18_data_dict['ID'].append(id)
                geos18_data_dict['Product_Name'].append(sub_sub_path[0])
                geos18_data_dict['Year'].append(sub_sub_path[1])
                geos18_data_dict['Day'].append(sub_sub_path[2])
                geos18_data_dict['Hour'].append(sub_sub_path[3])
                id += 1
    
    # Convert the dictionary into a pandas dataframe for easy handling
    geos18_data = pd.DataFrame(geos18_data_dict)
    write_logs(f"Returning metadata from GEOS18 Bucket: {geos18_data}")
    
    # Set up the database connection and create table if not exists
    database_file_name = 'airflow_scrape_data.db'
    ddl_file_name = 'airflow_geos18.sql'
    table_name = 'GEOS18'

    database_file_path = os.path.join(os.path.dirname(__file__), database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__), ddl_file_name)
    db = sqlite3.connect(database_file_path)

    # If database file path found return the updated metadata into GOES18 Table in the db
    if Path(database_file_path).is_file():
        write_logs(f"Database file found, saving GEOS18 metadata into GEOS18 Table")
        geos18_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
    
    # If database file path not found, create a db file and return the updated metadata into GOES18 Table
    else:
        write_logs(f"Database file not found, initializing database {database_file_name} and updating data into GEOS18 Table.")
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()        
        geos18_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
        cursor.executescript(sql_script)
    
    # Commit the queries in DB file
    db.commit()
    
    # Close DB file
    db.close()
    write_logs(f"Successfully Scraped GEOS18 Metadata and stored to Database file.")

def scrape_nexrad_metadata():
    nexrad_bucket_name = "noaa-nexrad-level2"
    nexrad_data_dict = {'ID': [], 'Year': [], 'Month': [], 'Day': [], 'NexRad_Station_Code': []}
    
    # Call function to write logs
    write_logs(f"Scraping NexRad Metadata into Database")

    id = 1
    years = ['2022','2023']
    
    for year in years:
        prefix = year + '/'
        result = s3client.list_objects(Bucket = nexrad_bucket_name, Prefix = prefix, Delimiter = '/')
        write_logs(f"Returning list of objects in NEXRAD Bucket for selected prefix {prefix}: {result}")

        # Loop through each object in the result object and get metadata
        for i in result.get('CommonPrefixes'):
            path = i.get('Prefix').split('/')
            prefix_2 = prefix + path[-2] + "/"
            sub_folder = s3client.list_objects(Bucket = nexrad_bucket_name, Prefix = prefix_2, Delimiter = '/')
            
            for j in sub_folder.get('CommonPrefixes'):
                sub_path = j.get('Prefix').split('/')
                prefix_3 = prefix_2 + sub_path[-2] + "/"
                sub_sub_folder = s3client.list_objects(Bucket = nexrad_bucket_name, Prefix = prefix_3, Delimiter = '/')

                for k in sub_sub_folder.get('CommonPrefixes'):
                    sub_sub_path = k.get('Prefix').split('/')
                    sub_sub_path = sub_sub_path[:-1]
                    nexrad_data_dict['ID'].append(id)
                    nexrad_data_dict['Year'].append(sub_sub_path[0])
                    nexrad_data_dict['Month'].append(sub_sub_path[1])
                    nexrad_data_dict['Day'].append(sub_sub_path[2])
                    nexrad_data_dict['NexRad_Station_Code'].append(sub_sub_path[3])
                    id += 1
    
    # Convert the dictionary into a pandas dataframe for easy handling
    nexrad_data = pd.DataFrame(nexrad_data_dict)
    write_logs(f"Returning metadata from NEXRAD Bucket: {nexrad_data}")

    # Set up the database connection and create table if not exists
    database_file_name = 'airflow_scrape_data.db'
    ddl_file_name = 'airflow_nexrad.sql'
    table_name = 'NEXRAD'

    database_file_path = os.path.join(os.path.dirname(__file__), database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__), ddl_file_name)
    db = sqlite3.connect(database_file_path)
    
    # If database file path found return the updated metadata into NexRad Table in the db
    if Path(database_file_path).is_file():
        write_logs(f"Database file found, saving NEXRAD metadata into NEXRAD Table")
        nexrad_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
    
    # If database file path not found, create a db file and return the updated metadata into NexRad Table
    else:
        write_logs(f"Database file not found, initializing database {database_file_name} and updating data into NEXRAD Table.")
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()        
        nexrad_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
        cursor.executescript(sql_script)
        
    # Commit the queries in DB file
    db.commit()
    
    # Close DB file
    db.close()
    write_logs(f"Successfully Scraped NEXRAD Metadata and stored to Database file.")

# Define a function to upload the database to S3 bucket
def upload_db_s3():
    s3res = boto3.resource('s3', region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))
    
    # Upload the database file to the S3 bucket
    s3res.Bucket(os.environ.get('USER_BUCKET_NAME')).upload_file("./dags/airflow_scrape_data.db", "data-store/airflow_scrape_data.db")
    
    # Define database file name and path and connect to database
    database_file_name = 'airflow_scrape_data.db'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    conn = sqlite3.connect(database_file_path, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    
    # Read data from the database tables GEOS18 and NEXRAD into pandas dataframes
    goes_df = pd.read_sql_query("SELECT * FROM GEOS18", conn)
    nexrad_df = pd.read_sql_query("SELECT * FROM NEXRAD", conn)

    # Upload the GEOS18 data to S3 bucket in CSV format
    s3client.put_object(Body=goes_df.to_csv(index=False), Bucket=os.environ.get('USER_BUCKET_NAME'), Key='data-store/goes18_data.csv')
    
    # Upload the NEXRAD data to S3 bucket in CSV format
    s3client.put_object(Body=nexrad_df.to_csv(index=False), Bucket=os.environ.get('USER_BUCKET_NAME'), Key='data-store/nexrad_data.csv')

    # Close the database connection and log the successful upload of database and data files to S3 bucket
    conn.close()
    write_logs(f"Successfully uploaded database and data files to S3 bucket.")

with dag:

    # Creating PythonOperator to scrape GEOS18 metadata and store it in a SQLite database
    scrape_geos18 = PythonOperator(   
    task_id='scrape_geos18',
    python_callable = scrape_geos18_metadata,
    provide_context=True,
    dag=dag,
    )

    # Creating PythonOperator to scrape NEXRAD metadata and store it in a SQLite database
    scrape_nexrad = PythonOperator(   
    task_id='scrape_nexrad',
    python_callable = scrape_nexrad_metadata,
    provide_context=True,
    dag=dag,
    )

    # Creating PythonOperator to upload SQLite database to S3
    upload_db = PythonOperator(   
    task_id='upload_db_to_s3',
    python_callable = upload_db_s3,
    provide_context=True,
    dag=dag,
    )

    # Defining the workflow by setting up the dependencies between tasks
    scrape_geos18 >> scrape_nexrad >> upload_db