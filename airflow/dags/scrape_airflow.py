import os
import re
import time
import boto3
import sqlite3
import requests
import pandas as pd
from pathlib import Path
from datetime import timedelta
from airflow.models import DAG
from botocore import UNSIGNED
from botocore.config import Config
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.models.param import Param
from airflow.operators.python_operator import PythonOperator
# from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator

base_path = "/opt/working_dir"
# data_dir = os.path.join(base_path, "News-Aggregator", "great_expectations", "data")
ge_root_dir = os.path.join(base_path, "great_expectations")

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

s3client = boto3.client('s3',
                    region_name='us-east-1',
                    config=Config(signature_version=UNSIGNED)
                    )

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

def scrape_nexradmap_metadata():
    nexrad_map_data_url = "https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt"
    nexradmap_data_dict = {'ID': [], 'Station_Code': [], 'State': [], 'County': [],'latitude': [], 'longitude': [],'elevation': []}
    write_logs(f"Scraping NexRadMap Metadata into Database")

    try:
        response = requests.get(nexrad_map_data_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err_http:
        write_logs(f"Exited due to HTTP error while accessing URL")
        raise SystemExit(err_http)
    except requests.exceptions.ConnectionError as err_conn:
        write_logs(f"Exited due to Connection error while accessing URL")
        raise SystemExit(err_conn)
    except requests.exceptions.Timeout as err_tim:
        write_logs(f"Exited due to Timeout error while accessing URL")
        raise SystemExit(err_tim)
    
    lines = response.text.split('\n')
    id = 0
    nexradmap = []
    for line in lines:
        line = line.strip()
        word_list = line.split(" ")
        if (word_list[-1].upper() == 'NEXRAD'):
            nexradmap.append(line)
    nexradmap = [i for i in nexradmap if 'UNITED STATES' in i]
    
    for station in nexradmap:
        id += 1
        station1 = station.split("  ")
        station1 =  [i.strip() for i in station1 if i != ""]
        station2 = station.split(" ")
        station2 =  [i.strip() for i in station2 if i != ""]
        nexradmap_data_dict['ID'].append(id)
        nexradmap_data_dict['Station_Code'].append(station1[0].split(" ")[1])
        for i in range(len(station1)):
            if (re.match(r'\b[A-Z][A-Z]\b',station1[i].strip())):
                nexradmap_data_dict['State'].append(station1[i][:2])
                nexradmap_data_dict['County'].append(station1[i][2:])
        for i in range(len(station2)):
            if (re.match(r'^-?[0-9]\d(\.\d+)?$',station2[i])):
                nexradmap_data_dict['latitude'].append(float(station2[i]))
                nexradmap_data_dict['longitude'].append(float(station2[i+1]))
                nexradmap_data_dict['elevation'].append(int(station2[i+2]))
                break
    
    nexradmap_data = pd.DataFrame(nexradmap_data_dict)
    write_logs(f"Returning metadata for NEXRAD Map Locations: {nexradmap_data}")

    # Set up the database connection and create table if not exists
    database_file_name = 'airflow_scrape_data.db'
    ddl_file_name = 'airflow_nexradmap.sql'
    table_name = 'NexradMap'

    database_file_path = os.path.join(os.path.dirname(__file__), database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__), ddl_file_name)
    db = sqlite3.connect(database_file_path)
    
    # If database file path found return the updated metadata into NexRad Table in the db
    if Path(database_file_path).is_file():
        write_logs(f"Database file found, saving NexradMap metadata into NexradMap Table")
        nexradmap_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
    
    # If database file path not found, create a db file and return the updated metadata into NexRad Table
    else:
        write_logs(f"Database file not found, initializing database {database_file_name} and updating data into NexradMap Table.")
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()        
        nexradmap_data.to_sql(table_name, db, if_exists = 'replace', index=False)
        cursor = db.cursor()
        cursor.executescript(sql_script)
        
    # Commit the queries in DB file
    db.commit()
    
    # Close DB file
    db.close()
    write_logs(f"Successfully Scraped NexradMap Metadata and stored to Database file.")

def upload_db_s3():
    s3res = boto3.resource('s3', region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))
    s3res.Bucket(os.environ.get('USER_BUCKET_NAME')).upload_file("./dags/airflow_scrape_data.db", "data-store/airflow_scrape_data.db")
    
    database_file_name = 'airflow_scrape_data.db'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    conn = sqlite3.connect(database_file_path, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    goes_df = pd.read_sql_query("SELECT * FROM GEOS18", conn)
    nexrad_df = pd.read_sql_query("SELECT * FROM NEXRAD", conn)
    nexradmap_df = pd.read_sql_query("SELECT * FROM NexradMap", conn)

    goes_df.to_csv(f"./working_dir/data/noaa_geos18.csv", sep=',', index=False)
    nexrad_df.to_csv(f"./working_dir/data/noaa_nexrad.csv", sep=',', index=False)
    nexradmap_df.to_csv(f"./working_dir/data/noaa_nexradmap.csv", sep=',', index=False)

    s3client.put_object(Body=goes_df.to_csv(index=False), Bucket=os.environ.get('USER_BUCKET_NAME'), Key='data-store/goes18_data.csv')
    s3client.put_object(Body=nexrad_df.to_csv(index=False), Bucket=os.environ.get('USER_BUCKET_NAME'), Key='data-store/nexrad_data.csv')
    s3client.put_object(Body=nexradmap_df.to_csv(index=False), Bucket=os.environ.get('USER_BUCKET_NAME'), Key='data-store/nexradmap_data.csv')

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

    # Creating PythonOperator to scrape NEXRAD metadata and store it in a SQLite database
    scrape_nexradmap = PythonOperator(   
    task_id='scrape_nexradmap',
    python_callable = scrape_nexradmap_metadata,
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
    scrape_geos18 >> scrape_nexrad >> scrape_nexradmap >> upload_db