import os
import boto3
import sqlite3
from dotenv import load_dotenv

#load env variables
load_dotenv()

s3client = boto3.client('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )

# Get the name of the S3 bucket from the environment variable
user_bucket = os.environ.get('USER_BUCKET_NAME')

# Get the current directory path
dir_path = os.path.dirname(os.path.realpath(__file__))

# Check if running in a CI environment
if (os.environ.get('CI_FLAG')=='True'):
    pass
else:
    s3client.download_file(user_bucket, 'data-store/airflow_scrape_data.db', f"{dir_path}/airflow_scrape_data.db")

async def get_database_file():
    """
    Establish a database connection to access the user data
    """
    # Establish a connection to the database file
    database_connection = sqlite3.connect('airflow_scrape_data.db')
    
    # Return the connection object
    return database_connection