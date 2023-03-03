import os
import time
import boto3
import pandas as pd
from sqlite3 import Connection
from jwt_api import get_current_user
from database_file import get_database_file
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, status, HTTPException, Depends

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
router = APIRouter(
    prefix="/noaa-database",
    tags=['NOAA-Database']
)

clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOGS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOGS_SECRET_KEY')
                        )

def write_logs(message: str):
    clientLogs.put_log_events(
        logGroupName = "Assignment-03",
        logStreamName = "API-Logs",
        logEvents = [
            {
                'timestamp' : int(time.time() * 1e3),
                'message' : message
            }
        ]
    )

@router.get('/goes18', status_code=status.HTTP_200_OK)
async def get_product_goes(db_conn : Connection = Depends(get_database_file), token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    query = "SELECT DISTINCT Product_Name FROM GEOS18"
    df_product = pd.read_sql_query(query, db_conn)
    product = df_product['Product_Name'].tolist()
    if (len(product)!=0):
        write_logs("API endpoint: /noaa-database/goes18\n Called by: " + get_current_user(token).username + " \n Response: 200 \nSuccess, Product_Name found")
        return product
    else:
        write_logs("API endpoint: /noaa-database/goes18\n Called by: " + get_current_user(token).username + " \n Response: 404 \nPlease make sure you entered valid product")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid product")

@router.get('/goes18/prod', status_code=status.HTTP_200_OK)
async def get_years_in_product_goes(product : str = 'ABI-L1b-RadC', db_conn : Connection = Depends(get_database_file), token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    query = "SELECT DISTINCT Year FROM GEOS18 WHERE Product_Name = " + "\'" + product + "\'"
    df_year = pd.read_sql_query(query, db_conn)
    years = df_year['Year'].tolist()
    if (len(years)!=0):
        write_logs("API endpoint: /noaa-database/goes18/prod\n Called by: " + get_current_user(token).username + " \n Response: 200 \nSuccess, Years found")
        return years
    else:
        write_logs("API endpoint: /noaa-database/goes18/prod\n Called by: " + get_current_user(token).username + " \n Response: 404 \nPlease make sure you entered valid year")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid product")

@router.get('/goes18/prod/year', status_code=status.HTTP_200_OK)
async def get_days_in_year_goes(year : str, product : str = 'ABI-L1b-RadC', db_conn : Connection = Depends(get_database_file), token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    query = "SELECT DISTINCT Day FROM GEOS18 WHERE Year = " + "\'" + year + "\'" + "AND Product_Name = " + "\'" + product + "\'"
    df_day = pd.read_sql_query(query, db_conn)
    days = df_day['Day'].tolist()
    if (len(days)!=0):
        write_logs("API endpoint: /noaa-database/goes18/prod/year\n Called by: " + get_current_user(token).username + " \n Response: 200 \nSuccess, Days found")
        return days
    else:
        write_logs("API endpoint: /noaa-database/goes18/prod/year\n Called by: " + get_current_user(token).username + " \n Response: 404 \nPlease make sure you entered valid day")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/goes18/prod/year/day', status_code=status.HTTP_200_OK)
async def get_hours_in_day_goes(day : str, year : str, product : str = 'ABI-L1b-RadC', db_conn : Connection = Depends(get_database_file), token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    query = "SELECT DISTINCT Hour FROM GEOS18 WHERE Day = " + "\'" + day + "\'" + "AND Year = " + "\'" + year + "\'" + "AND Product_Name = " + "\'" + product + "\'"
    df_hour = pd.read_sql_query(query, db_conn)
    hours = df_hour['Hour'].tolist()
    if (len(hours)!=0):
        write_logs("API endpoint: /noaa-database/goes18/prod/year/day\n Called by: " + get_current_user(token).username + " \n Response: 200 \nSuccess, Hours found")
        return hours
    else:
        write_logs("API endpoint: /noaa-database/goes18/prod/year/day\n Called by: " + get_current_user(token).username + " \n Response: 404 \nPlease make sure you entered valid hour")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/nexrad', status_code=status.HTTP_200_OK)
async def get_years_nexrad(db_conn : Connection = Depends(get_database_file), token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    query = "SELECT DISTINCT Year FROM NEXRAD"
    df_year = pd.read_sql_query(query, db_conn)
    years = df_year['Year'].tolist()
    if (len(years)!=0):
        write_logs("API endpoint: /noaa-database/nexrad\n Called by: " + get_current_user(token).username + " \n Response: 200 \nSuccess, Year found")
        return years
    else:
        write_logs("API endpoint: /noaa-database/nexrad\n Called by: " + get_current_user(token).username + " \n Response: 404 \nPlease make sure you entered valid years")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/nexrad/year', status_code=status.HTTP_200_OK)
async def get_months_in_year_nexrad(year : str, db_conn : Connection = Depends(get_database_file), token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    query = "SELECT DISTINCT Month FROM NEXRAD WHERE Year = " + "\'" + year + "\'"
    df_month = pd.read_sql_query(query, db_conn)
    months = df_month['Month'].tolist()
    if (len(months)!=0):
        write_logs("API endpoint: /noaa-database/nexrad/year\n Called by: " + get_current_user(token).username + " \n Response: 200 \nSuccess, Months found")
        return months
    else:
        write_logs("API endpoint: /noaa-database/nexrad/year\n Called by: " + get_current_user(token).username + " \n Response: 404 \nPlease make sure you entered valid months")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/nexrad/year/month', status_code=status.HTTP_200_OK)
async def get_days_in_month_nexrad(month : str, year: str, db_conn : Connection = Depends(get_database_file), token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    query = "SELECT DISTINCT Day FROM NEXRAD WHERE Month = " + "\'" + month + "\'" + "AND Year = " + "\'" + year + "\'"
    df_day = pd.read_sql_query(query, db_conn)
    days = df_day['Day'].tolist()
    if (len(days)!=0):
        write_logs("API endpoint: /noaa-database/nexrad/year/month\n Called by: " + get_current_user(token).username + " \n Response: 200 \nSuccess, Days found")
        return days
    else:
        write_logs("API endpoint: /noaa-database/nexrad/year/month\n Called by: " + get_current_user(token).username + " \n Response: 404 \nPlease make sure you entered valid days")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/nexrad/year/month/day', status_code=status.HTTP_200_OK)
async def get_stations_for_day_nexrad(day : str, month : str, year : str, db_conn : Connection = Depends(get_database_file), token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    query = "SELECT DISTINCT NexRad_Station_Code FROM NEXRAD WHERE Day = " + "\'" + day + "\'" + "AND Month = " + "\'" + month + "\'" + " AND Year =" + "\'" + year + "\'"
    df_station = pd.read_sql_query(query, db_conn)
    stations = df_station['NexRad_Station_Code'].tolist()
    if (len(stations)!=0):
        write_logs("API endpoint: /noaa-database/nexrad/year/month/day\n Called by: " + get_current_user(token).username + " \n Response: 200 \nSuccess, Station_Codes found")
        return stations
    else:
        write_logs("API endpoint: /noaa-database/nexrad/year/month/day\n Called by: " + get_current_user(token).username + " \n Response: 404 \nPlease make sure you entered valid station codes")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/mapdata', status_code=status.HTTP_200_OK)
async def get_nexrad_mapdata(db_conn : Connection = Depends(get_database_file), token: str = Depends(oauth2_scheme)):
    user_id = get_current_user(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    map_dict = {}
    query = "SELECT * FROM NexradMap"
    df_mapdata = pd.read_sql_query(query, db_conn)
    
    stations = df_mapdata['Station_Code'].tolist()
    states = df_mapdata['State'].tolist()
    counties = df_mapdata['County'].tolist()
    latitude = df_mapdata['latitude'].tolist()
    longitude = df_mapdata['longitude'].tolist()
    elevation = df_mapdata['elevation'].tolist()
    
    map_dict['Station_Code'] = stations
    map_dict['State'] = states
    map_dict['County'] = counties
    map_dict['latitude'] = latitude
    map_dict['longitude'] = longitude
    map_dict['elevation'] = elevation

    if (len(df_mapdata.index)!=0):
        write_logs("API endpoint: /noaa-database/mapdata\n Called by: " + get_current_user(token).username + " \n Response: 200 \nSuccess, Map Data found")
        return map_dict
    else:
        write_logs("API endpoint: /noaa-database/mapdata\n Called by: " + get_current_user(token).username + " \n Response: 404 \nPlease make sure you have valid map database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Unable to fetch mapdata")