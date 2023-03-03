import os
import time
import boto3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlite3 import Connection
from datetime import datetime, timedelta
import schemas, user_data, user_db_model
from database_file import get_database_file, get_user_data_file
from fastapi import FastAPI, APIRouter, status, HTTPException, Depends
from jwt_api import verify, bcrypt, create_access_token, get_current_user

dotenv_path = Path('./.env')
load_dotenv(dotenv_path)
router = APIRouter(
    prefix="/user/logs",
    tags=['User-Logs']
)

@router.get('/admin-account', status_code=status.HTTP_200_OK)
async def get_admin_logs(current_user: schemas.User = Depends(get_current_user), user_data : Connection = Depends(get_user_data_file)):
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOGS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOGS_SECRET_KEY')
                        )

    log_group_name = 'Assignment-03'
    log_stream_name = 'API-Logs'
    query = f"fields @timestamp, @message | sort @timestamp asc | filter @logStream='{log_stream_name}'"
    response = clientLogs.start_query(
        logGroupName=log_group_name,
        startTime=0,
        endTime=int(time.time() * 1000),
        queryString=query,
        limit=10000
    )

    query_id = response['queryId']
    response = None
    while response is None or response['status'] == 'Running':
        time.sleep(1)
        response = clientLogs.get_query_results(
            queryId = query_id
        )

    events = []
    for event in response['results']:
        timestamp = datetime.strptime(event[0]['value'], '%Y-%m-%d %H:%M:%S.%f')
        message = event[1]['value']
        log_messages = message.split(":")
        api_endpoint = log_messages[1].strip().split()[0]
        current_user = log_messages[2].strip().split()[0]
        user_response = log_messages[3].strip().split()[0]
        events.append((timestamp, message, api_endpoint, current_user, user_response))
    
    request_log_data = pd.DataFrame(events, columns = ['Timestamp', 'Message', 'API_Endpoint', 'User', 'Response'])
    return request_log_data

@router.get('/user-account', status_code=status.HTTP_200_OK)
async def get_user_logs(username : str, current_user: schemas.User = Depends(get_current_user), user_data : Connection = Depends(get_user_data_file)):
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOGS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOGS_SECRET_KEY')
                        )

    log_group_name = 'Assignment-03'
    log_stream_name = 'API-Logs'
    query = f"fields @timestamp, @message | sort @timestamp asc | filter @logStream='{log_stream_name}'"
    response = clientLogs.start_query(
        logGroupName=log_group_name,
        startTime=0,
        endTime=int(time.time() * 1000),
        queryString=query,
        limit=10000
    )

    query_id = response['queryId']
    response = None
    while response is None or response['status'] == 'Running':
        time.sleep(1)
        response = clientLogs.get_query_results(
            queryId = query_id
        )

    events = []
    for event in response['results']:
        timestamp = datetime.strptime(event[0]['value'], '%Y-%m-%d %H:%M:%S.%f')
        message = event[1]['value']
        log_messages = message.split(":")
        current_user = log_messages[2].strip().split()[0]
        if (current_user == username):
            api_endpoint = log_messages[1].strip().split()[0]
            user_response = log_messages[3].strip().split()[0]
            events.append((timestamp, message, api_endpoint, current_user, user_response))
        else:
            pass

    request_log_data = pd.DataFrame(events, columns = ['Timestamp', 'Message', 'API_Endpoint', 'User', 'Response'])
    return request_log_data

@router.get('/latest', status_code=status.HTTP_200_OK)
async def get_latest_user_logs(username : str, current_user: schemas.User = Depends(get_current_user), userdb_conn : Connection = Depends(get_user_data_file)):
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOGS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOGS_SECRET_KEY')
                        )

    log_group_name = 'Assignment-03'
    log_stream_name = 'API-Logs'
    start_time = datetime.utcnow() - timedelta(hours=1)
    startTime = int(start_time.timestamp() * 1000)
    query = f"fields @timestamp, @message | sort @timestamp asc | filter @logStream='{log_stream_name}'"
    response = clientLogs.start_query(
        logGroupName=log_group_name,
        startTime=startTime,
        endTime=int(time.time() * 1000),
        queryString=query,
        limit=10000
    )

    query_id = response['queryId']
    response = None
    while response is None or response['status'] == 'Running':
        time.sleep(1)
        response = clientLogs.get_query_results(
            queryId = query_id
        )

    events = []
    for event in response['results']:
        timestamp = datetime.strptime(event[0]['value'], '%Y-%m-%d %H:%M:%S.%f')
        message = event[1]['value']
        log_messages = message.split(":")
        current_user = log_messages[2].strip().split()[0]
        if (current_user == username):
            api_endpoint = log_messages[1].strip().split()[0]
            user_response = log_messages[3].strip().split()[0]
            events.append((timestamp, message, api_endpoint, current_user, user_response))
        else:
            pass

    request_log_data = pd.DataFrame(events, columns = ['Timestamp', 'Message', 'API_Endpoint', 'User', 'Response'])
    return request_log_data