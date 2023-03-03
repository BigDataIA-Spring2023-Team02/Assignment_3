import os
import boto3
import sqlite3
from dotenv import load_dotenv

load_dotenv()
s3client = boto3.client('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )

user_bucket = os.environ.get('USER_BUCKET_NAME')
dir_path = os.path.dirname(os.path.realpath(__file__))

if (os.environ.get('CI_FLAG')=='True'):
    pass
else:
    s3client.download_file(user_bucket, 'data-store/airflow_scrape_data.db', f"{dir_path}/airflow_scrape_data.db")

async def get_database_file():
    database_connection = sqlite3.connect('airflow_scrape_data.db')
    return database_connection

async def get_user_data_file():
    user_connection = sqlite3.connect('user_data.db')
    return user_connection