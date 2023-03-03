import re
import os
import boto3
import requests
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
    prefix="/aws-s3-fetchfile",
    tags=['aws-s3-fetchfile']
)

# Decorator for the HTTP POST method for the /goes18 endpoint
@router.post('/goes18', status_code=status.HTTP_200_OK)
async def generate_goes_url(file_input : str, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # create a boto3 client object for logging
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )
    
    # specify the input URL for GOES-18 bucket
    input_url = "https://noaa-goes18.s3.amazonaws.com/"
    
    # clean up the file name by removing any whitespaces
    file_name = file_input.strip()
    
    # match the file name with the required pattern using regular expression
    if (re.match(r'[O][R][_][A-Z]{3}[-][A-Za-z0-9]{2,3}[-][A-Za-z0-9]{4,6}[-][A-Z0-9]{2,5}[_][G][1][8][_][s][0-9]{14}[_][e][0-9]{14}[_][c][0-9]{14}\b', file_name)):
        file_name = file_name.split("_")
        file_split = file_name[1].split('-')
        
        # Extracting all non-digit characters from the 3rd element of the file_split list
        no_digits = []
        for i in file_split[2]:
            if not i.isdigit():
                no_digits.append(i)
        
        # Joining all the non-digit characters into a string
        str_2 = ''.join(no_digits)
        
        # Extracting year, day and hour from the 4th element of the file_name list
        year = file_name[3][1:5]
        day = file_name[3][5:8]
        hour = file_name[3][8:10]
        
        # Constructing the final url by concatenating all the extracted elements in the required format
        final_url = input_url + file_split[0] + '-' + file_split[1] + '-' + str_2 + '/' + year + '/' + day + '/' + hour + '/' + file_input
        
        # check if the URL is valid by making a GET request
        response = requests.get(final_url)
        
        # if the file is not found at the specified URL, raise a 404 error
        if(response.status_code == 404):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail= "No such file exists at GOES18 location")
        
        # if the URL is valid, return it
        return final_url
    
    # if the file name does not match the required pattern, raise a 400 error
    else:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail= "Invalid filename format for GOES18")

# Decorator for the HTTP POST method for the /nexrad endpoint
@router.post('/nexrad', status_code=status.HTTP_200_OK)
async def generate_nexrad_url(file_input : str, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # create a boto3 client object for logging
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    # specify the input URL for NEXRAD bucket
    input_url = "https://noaa-nexrad-level2.s3.amazonaws.com/"
    
    # clean up the file name by removing any whitespaces
    file_name = file_input.strip()
    
    # match the file name with the required pattern using regular expression
    if (re.match(r'[A-Z]{3}[A-Z0-9][0-9]{8}[_][0-9]{6}[_]{0,1}[A-Z]{0,1}[0-9]{0,2}[_]{0,1}[A-Z]{0,3}\b', file_name)):
        # Construct the final URL to the file
        final_url = input_url+file_name[4:8]+"/"+file_name[8:10]+"/"+file_name[10:12]+"/"+file_name[:4]+"/"+file_input
        
        # Send an HTTP GET request to the constructed URL to check if the file exists
        response = requests.get(final_url)
        
        # if the file is not found at the specified URL, raise a 404 error
        if(response.status_code == 404):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail= "No such file exists at NEXRAD location")
        
        # Return the final URL if the file exists
        return final_url

    # if the file name does not match the required pattern, raise a 400 error
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail= "Invalid filename format for NEXRAD")