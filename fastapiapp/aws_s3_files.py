import os
import boto3
from pathlib import Path
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, status, HTTPException, Depends
from jwt_api import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#set path for env variables
dotenv_path = Path('./.env')

#load env variables
load_dotenv(dotenv_path)

# create an API router object with prefix and tags
router = APIRouter(
    prefix="/aws-s3-files",
    tags=['aws-s3-files']
)

# Decorator for the HTTP POST method for the /goes18 endpoint to list all the files available in goes18 bucket
@router.get('/goes18', status_code=status.HTTP_200_OK)
async def list_files_in_goes18_bucket(year : str, day : str, hour : str, product : str = "ABI-L1b-RadC", token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Set the name of the GOES-18 bucket and initialize the S3 client and resource objects
    geos_bucket_name = "noaa-goes18"
    s3client = boto3.client('s3',
                            region_name = 'us-east-1',
                            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                            )
    s3resource = boto3.resource('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )
    
    # Initialize the AWS CloudWatch logs client
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )
    
    # Initialize an empty list to hold the file names
    file_list = []

    # Set the prefix for the specified product, year, day, and hour
    prefix = product+'/'+year+'/'+day+'/'+hour+'/'
    
    # Use the S3 client to list objects in the GOES-18 bucket with the specified prefix
    geos_bucket = s3client.list_objects(Bucket = geos_bucket_name, Prefix = prefix).get('Contents')

    # Iterate through the returned objects and append the file names to the file_list
    for objects in geos_bucket:
        file_path = objects['Key']
        file_path = file_path.split('/')
        file_list.append(file_path[-1])
    
    # If any files are found, return the list of file names, otherwise raise a 404 error
    if (len(file_list)!=0):
        # if the URL is valid, return it
        return file_list
    else:
        # if the file is not found at the specified URL, raise a 404 error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Unable to fetch filenames from S3 bucket")

# Decorator for the HTTP POST method for the /nexrad endpoint to list all the files available in nexrad bucket
@router.get('/nexrad', status_code=status.HTTP_200_OK)
async def list_files_in_nexrad_bucket(year : str, month : str, day : str, nexrad_station : str, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Set the name of the NEXRAD bucket and initialize the S3 client and resource objects
    nexrad_bucket_name = "noaa-nexrad-level2"
    s3client = boto3.client('s3',
                            region_name = 'us-east-1',
                            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                            )
    s3resource = boto3.resource('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )
    
    # Initialize the AWS CloudWatch logs client
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )
    # Initialize an empty list to hold the file names
    file_list = []

    # Set the prefix for the specified year, month, day and nexrad station code
    prefix = year+'/'+month+'/'+day+'/'+nexrad_station+'/'
    
    # Use the S3 client to list objects in the NexRad bucket with the specified prefix
    nexrad_bucket = s3client.list_objects(Bucket = nexrad_bucket_name, Prefix = prefix).get('Contents')
    
    # Iterate through the returned objects and append the file names to the file_list
    for objects in nexrad_bucket:
        file_path = objects['Key']
        file_path = file_path.split('/')
        file_list.append(file_path[-1])
    
    # If any files are found, return the list of file names, otherwise raise a 404 error
    if (len(file_list)!=0):
        # if the URL is valid, return it
        return file_list
    else:
        # if the file is not found at the specified URL, raise a 404 error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Unable to fetch filenames from S3 bucket")

# Decorator for the HTTP POST method for the /goes18/copyfile endpoint to copy the files from goes18 to user bucket
@router.post('/goes18/copyfile', status_code=status.HTTP_200_OK)
async def copy_goes_file_to_user_bucket(file_name : str, product : str, year : str, day : str, hour : str, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Set the name of the GOES-18 bucket and initialize the S3 client and resource objects
    geos_bucket_name = "noaa-goes18"
    s3client = boto3.client('s3',
                            region_name = 'us-east-1',
                            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                            )
    s3resource = boto3.resource('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )
    
    # Initialize the AWS CloudWatch logs client
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )
    
    try:
        # Set up destination bucket
        destination_bucket = s3resource.Bucket(os.environ.get('USER_BUCKET_NAME'))
        
        # Set up parameters for copying file
        selected_file_key = product+'/'+year+'/'+day+'/'+hour+'/'+file_name
        dest_folder = 'GOES18/'
        dest_key = dest_folder + file_name
        
        # url to copy the file to user s3 bucket
        url_to_mys3 = 'https://damg-7245-projects.s3.amazonaws.com/' + dest_key
        copy_source = {
            'Bucket': geos_bucket_name,
            'Key': selected_file_key
            }
        
        # Check if file already exists in destination bucket
        for file in destination_bucket.objects.all():
            if(file.key == dest_key):
                # Return url of destination bucket
                return url_to_mys3
        
        # Copy file to destination bucket
        destination_bucket.copy(copy_source, dest_key)
        
        # Return url of destination bucket
        return url_to_mys3

    except:
        # Raise an exception if the file cannot be copied
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Unable to copy file")

# Decorator for the HTTP POST method for the /nexrad/copyfile endpoint to copy the files from nexrad to user bucket
@router.post('/nexrad/copyfile', status_code=status.HTTP_200_OK)
def copy_nexrad_file_to_user_bucket(file_name : str, year : str, month : str, day : str, nexrad_station : str, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Set up S3 client and resource objects
    nexrad_bucket_name = "noaa-nexrad-level2"
    s3client = boto3.client('s3',
                            region_name = 'us-east-1',
                            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                            )
    s3resource = boto3.resource('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )
    
    try:
        # Set up destination bucket
        destination_bucket = s3resource.Bucket(os.environ.get('USER_BUCKET_NAME'))
        
        # Set up parameters for copying file
        selected_file_key = year+'/'+month+'/'+day+'/'+nexrad_station+'/'+file_name
        dest_folder = 'NEXRAD/'
        dest_key = dest_folder + file_name
        
        # url to copy the file to user s3 bucket
        url_to_mys3 = 'https://damg-7245-projects.s3.amazonaws.com/' + dest_key
        copy_source = {
            'Bucket': nexrad_bucket_name,
            'Key': selected_file_key
            }
        
        # Check if file already exists in destination bucket
        for file in destination_bucket.objects.all():
            if(file.key == dest_key):
                return url_to_mys3
        
        # Copy file to destination bucket
        destination_bucket.copy(copy_source, dest_key)
        
        # Return url of destination bucket
        return url_to_mys3

    except:
        # Raise an exception if the file cannot be copied
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Unable to copy file")