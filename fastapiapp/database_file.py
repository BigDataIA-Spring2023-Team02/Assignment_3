import os
import sqlite3

# Get the name of the S3 bucket from the environment variable
user_bucket = os.environ.get('USER_BUCKET_NAME')

# Get the current directory path
dir_path = os.path.dirname(os.path.realpath(__file__))

# Check if running in a CI environment
if (os.environ.get('CI_FLAG')=='True'):
    # Do nothing for now
    pass

async def get_database_file():
    # Establish a connection to the database file
    database_connection = sqlite3.connect('sql_scraped_database.db')
    
    # Return the connection object
    return database_connection