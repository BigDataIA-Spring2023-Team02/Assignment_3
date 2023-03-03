import streamlit as st
import boto3
import pandas as pd
import json
import requests
import os
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image
import numpy as np
import plotly.express as px

#load env variables
load_dotenv()

API_URL = "http://127.0.0.1:8080"

#authenticate S3 client for logging with your user credentials that are stored in your .env config file
clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

def dashboard_admin_main():
    st.title("API Dashboard-Admin")
    st.markdown(
        """
        <style>
            .title {
                text-align: center;
                color: #2F80ED;
            }
        </style>
        <h2 class="title">View application API calls data through dashboard</h2>
        <p></p>
        """,
        unsafe_allow_html=True,
    )

    header = {}
    header['Authorization'] = f"Bearer {st.session_state['access_token']}"
    response = requests.request("GET", f"{API_URL}/logs/admin", headers=header)  #call to relevant fastapi endpoint with authorization
    logs_resp = json.loads(response.text)   #store log responses from api

    if response.status_code == 200:
        df_requests = pd.DataFrame({
        'timestamp': logs_resp['timestamp'].values(),   
        'user': logs_resp['user'].values(),
        'endpoint': logs_resp['endpoint'].values(),
        'response': logs_resp['response'].values(),

        }, index = np.arange(len(logs_resp['timestamp'].values()))) #set values from log response api
        df_requests["timestamp"] = pd.to_datetime(df_requests["timestamp"]) #cover timestamp
    
        #display dashboard options
        options = ['User Requests', 'Total API calls yesterday', 'Avg Calls Last Week', 'Success vs Failed Calls', 'Endpoint Calls']
        choice = st.sidebar.selectbox('Select option', options)
        
        if choice == 'User Requests':
            #creating figure for Plotting a line chart of count of request by each user against time (date)
            fig_user_requests = go.Figure()
            for user in df_requests['user'].unique():
                df_count = df_requests.groupby([pd.Grouper(key='timestamp', freq='D'), 'user']).count()['endpoint'].reset_index()   #group by date and user and count the number of requests
                fig_user_requests = px.line(df_count, x='timestamp', y='endpoint', color='user', title='Request Count by User') #plot the line chart
        
            st.plotly_chart(fig_user_requests)  #display as plotly chart

        elif choice == 'Total API calls yesterday':
            #creating Metric for total API calls the previous day
            now = datetime.now()
            yesterday = (now - timedelta(days=1)).date()
            previous_day_df = df_requests.loc[df_requests["timestamp"].dt.date == yesterday]    #filter logs for all events yesterday
            total_calls_yesterday = previous_day_df["endpoint"].count()     #get the total number of API calls
            
            st.metric('Total API Calls (previous day)', total_calls_yesterday)  #display metric

        elif choice == 'Avg Calls Last Week':
            #creating Metric to show total average calls during the last week
            today = datetime.now().date()
            one_week_ago = today - timedelta(days=7)
            last_week_df = df_requests.loc[(df_requests["timestamp"].dt.date >= one_week_ago) & (df_requests["timestamp"].dt.date <= today)]    #filter the dataframe for the last week
            total_calls_last_week = last_week_df["endpoint"].count()     #calculate the total number of API calls during the last week
            days_in_last_week = (today - one_week_ago).days     #calculate the number of days in the last week
            average_calls_per_day_last_week = total_calls_last_week / days_in_last_week #calculate the average number of API calls per day during the last week
            
            st.metric('Avg Calls Last Week', average_calls_per_day_last_week)   #display metric

        elif choice == 'Success vs Failed Calls':
            #doing Comparison of Success ( 200 response code) and Failed request calls(ie non 200 response codes)
            num_success = len(df_requests[df_requests['response'] == '200'])    #filter for success code 200 records
            num_failed = len(df_requests) - num_success     #all others are failed calls

            st.metric('Successful Calls', num_success)  #display metric
            st.metric('Failed Calls', num_failed)   #display metric

        elif choice == 'Endpoint Calls':
            #creating figure for Each endpoint total number of calls
            fig_endpoint_calls = go.Figure()
            fig_endpoint_calls = px.histogram(df_requests, x='endpoint', title='Total Number of Calls per Endpoint')
            fig_endpoint_calls.update_layout(xaxis_title='Endpoint', yaxis_title='Number of Calls')
            endpoint_calls_total = len(df_requests) #also display overall call count
            
            st.plotly_chart(fig_endpoint_calls) #display as plotly chart
            st.metric('Total endpoint calls', endpoint_calls_total) #display metric
        
    else: #elif response.status_code == 401:   #when token is not authorized
        st.error("Session token expired, please login again")   #display error
        st.stop()

def dashboard_user_main():
    
    """Function called when DASHBOARD page opened from a user login on streamlit application UI. Allows user to view
    the dashboard analytcis for API endpoints
    -----
    Input parameters:
    None
    -----
    Returns:
    Nothing
    """

    st.title("User API Dashboard")
    st.markdown(
        """
        <style>
            .title {
                text-align: center;
                color: #2F80ED;
            }
        </style>
        <h2 class="title">View application API calls data through dashboard</h2>
        <p></p>
        """,
        unsafe_allow_html=True,
    )

    header = {}
    header['Authorization'] = f"Bearer {st.session_state['access_token']}"
    response = requests.request("GET", f"{API_URL}/logs/user?username={st.session_state['username']}", headers=header)  #call to relevant fastapi endpoint with authorization
    
    if response.status_code == 200:

        logs_resp = json.loads(response.text)   #store log responses from api
        df_requests = pd.DataFrame({
            'timestamp': logs_resp['timestamp'].values(),
            'user': logs_resp['user'].values(),
            'endpoint': logs_resp['endpoint'].values(),
            'response': logs_resp['response'].values(),
        }, index = np.arange(len(logs_resp['timestamp'].values()))) #set values from log response api
        df_requests["timestamp"] = pd.to_datetime(df_requests["timestamp"]) #cover timestamp
        
        #display dashboard options
        options = ['User Requests', 'Total API calls yesterday', 'Avg Calls Last Week', 'Success vs Failed Calls', 'Endpoint Calls']
        choice = st.sidebar.selectbox('Select option', options)
        
        if choice == 'User Requests':
            #creating figure for Plotting a line chart of count of request by each user against time (date)
            fig_user_requests = go.Figure()
            for user in df_requests['user'].unique():
                df_count = df_requests.groupby([pd.Grouper(key='timestamp', freq='D'), 'user']).count()['endpoint'].reset_index()   #group by date and user and count the number of requests
                fig_user_requests = px.line(df_count, x='timestamp', y='endpoint', color='user', title='Request Count by User') #plot the line chart
            
            st.plotly_chart(fig_user_requests)  #display as plotly chart

        elif choice == 'Total API calls yesterday':
            #creating Metric for total API calls the previous day
            now = datetime.now()
            yesterday = (now - timedelta(days=1)).date()
            previous_day_df = df_requests.loc[df_requests["timestamp"].dt.date == yesterday]    #filter logs for all events yesterday
            total_calls_yesterday = previous_day_df["endpoint"].count()     #get the total number of API calls
            
            st.metric('Total API Calls (previous day)', total_calls_yesterday)  #display metric

        elif choice == 'Avg Calls Last Week':
            #creating Metric to show total average calls during the last week
            today = datetime.now().date()
            one_week_ago = today - timedelta(days=7)
            last_week_df = df_requests.loc[(df_requests["timestamp"].dt.date >= one_week_ago) & (df_requests["timestamp"].dt.date <= today)]    #filter the dataframe for the last week
            total_calls_last_week = last_week_df["endpoint"].count()     #calculate the total number of API calls during the last week
            days_in_last_week = (today - one_week_ago).days     #calculate the number of days in the last week
            average_calls_per_day_last_week = total_calls_last_week / days_in_last_week #calculate the average number of API calls per day during the last week

            st.metric('Avg Calls Last Week', average_calls_per_day_last_week)   #display metric

        elif choice == 'Success vs Failed Calls':
            #doing Comparison of Success ( 200 response code) and Failed request calls(ie non 200 response codes)
            num_success = len(df_requests[df_requests['response'] == '200'])    #filter for success code 200 records
            num_failed = len(df_requests) - num_success     #all others are failed calls

            st.metric('Successful Calls', num_success)  #display metric
            st.metric('Failed Calls', num_failed)   #display metric

        elif choice == 'Endpoint Calls':
            #creating figure for Each endpoint total number of calls
            fig_endpoint_calls = go.Figure()
            fig_endpoint_calls = px.histogram(df_requests, x='endpoint', title='Total Number of Calls per Endpoint')
            fig_endpoint_calls.update_layout(xaxis_title='Endpoint', yaxis_title='Number of Calls')
            endpoint_calls_total = len(df_requests) #also display overall call count
        
            st.plotly_chart(fig_endpoint_calls) #display as plotly chart
            st.metric('Total endpoint calls', endpoint_calls_total) #display metric

    else:  #when token is not authorized
        st.error("Session token expired, please login again")   #display error
        st.stop()

def goes_main():

    """Function called when GOES-18 page opened from streamlit application UI. Allows user to select action 
    they wish to perform: search and download GOES-18 files by fields or search for URL by filename.
    -----
    Input parameters:
    None
    -----
    Returns:
    Nothing
    """

    st.title("GOES-18 Satellite File Downloader")
    st.markdown(
        """
        <style>
            .title {
                text-align: center;
                color: #2F80ED;
            }
        </style>
        <h2 class="title">Find the latest GOES Radar Data</h2>
        <p></p>
        """,
        unsafe_allow_html=True,
    )

    #search options
    download_option = st.sidebar.radio ("Use following to search for GOES radar data:",['Search by entering fields', 'Search by filename'])

    #search by fields
    if (download_option == "Search by entering fields"):
        st.write("Select all options in this form to download ")
        #bring in metadata from database to populate fields
        with st.spinner('Loading...'):
            header = {}
            header['Authorization'] = f"Bearer {st.session_state['access_token']}"
            response = requests.request("GET", f"{API_URL}/database/goes18", headers=header)    #call to relevant fastapi endpoint
        if response.status_code == 200:
            have_limit_flag = False
            with st.spinner("Loading..."): #spinner element
                header = {}
                header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                user_plan_response = requests.request("GET", f"{API_URL}/user/details?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
            if user_plan_response.status_code == 200:
                user_plan_resp = json.loads(user_plan_response.text)
                try:
                    api_calls = requests.request("GET", f"{API_URL}/logs/latest?username={st.session_state['username']}", headers=header)
                except:
                    st.error("Service unavailable, please try again later") #in case the API is not running
                    st.stop()   #stop the application   
                if api_calls.status_code == 200:
                    latest_logs_resp = json.loads(api_calls.text)   #store log responses from api
                    api_calls_in_last_hour = len(latest_logs_resp['timestamp']) #set values from log response api
                    
                    if (user_plan_resp == ["Free"]):
                        if (int(api_calls_in_last_hour) >= 10):
                            st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                            st.write("Do you wish to upgrade?")
                            if (st.button("Yes")):
                                #call api for upgrading user plan
                                limit_chk = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                                if limit_chk.status_code == 200:
                                    st.success("Plan upgraded, please continue.")    #display success message
                                    #refresh app
                                    with st.spinner("Loading..."): 
                                        st.experimental_rerun()
                            if (st.button("No")):
                                st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                                st.experimental_rerun()

                        else:   #if hourly plan limit not exhausted
                            have_limit_flag = True
        
                    elif (user_plan_resp == ["Gold"]):
                        if (int(api_calls_in_last_hour) >= 15):
                            st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                            st.write("Do you wish to upgrade?")
                            if (st.button("Yes")):
                                #call api for upgrading user plan
                                limit_chk2 = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                                if limit_chk2.status_code == 200:
                                    st.success("Plan upgraded, please continue.")    #display success message
                                    #refresh app
                                    with st.spinner("Loading..."): 
                                        st.experimental_rerun()
                            if (st.button("No")):
                                st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                                st.experimental_rerun()

                        else:   #if hourly plan limit not exhausted
                            have_limit_flag = True
            
                    elif (user_plan_resp == ['Platinum']):
                        have_limit_flag = True
            
                    else:   #then admin user
                        have_limit_flag = True
        elif response.status_code == 401:   #when token is not authorized
            st.error("Session token expired, please login again")   #display error
            st.stop()
        else:
            st.error("Database not populated. Please come back later!")
            st.stop()

        if (have_limit_flag):
            json_data = json.loads(response.text)
            product_selected = json_data    #store response data
        else:
            st.stop()   #do not go any further

        #define product box
        product_box = st.selectbox("Product name: ", product_selected, disabled = True, key="selected_product")
        with st.spinner('Loading...'):
            header = {}
            header['Authorization'] = f"Bearer {st.session_state['access_token']}"
            response = requests.request("GET", f"{API_URL}/database/goes18/prod?product={product_box}", headers=header) #call to relevant fastapi endpoint
        if response.status_code == 200:
            json_data = json.loads(response.text)
            year_list = json_data   #store response data
        elif response.status_code == 401:   #when token is not authorized
            st.error("Session token expired, please login again")   #display error
            st.stop()
        else:
            st.error("Incorrect input given, please change")
        #define year box
        year_box = st.selectbox("Year for which you are looking to get data for: ", ["--"]+year_list, key="selected_year")

        if (year_box == "--"):
            st.warning("Please select an year!")
        else:
            with st.spinner('Loading...'):
                header = {}
                header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                response = requests.request("GET", f"{API_URL}/database/goes18/prod/year?year={year_box}&product={product_box}", headers=header)    #call to relevant fastapi endpoint
            if response.status_code == 200:
                json_data = json.loads(response.text)
                day_list = json_data    #store response data
            elif response.status_code == 401:   #when token is not authorized
                st.error("Session token expired, please login again")   #display error
                st.stop()
            else:
                st.error("Incorrect input given, please change")
            #define day box
            day_box = st.selectbox("Day within year for which you want data: ", ["--"]+day_list, key="selected_day")
            if (day_box == "--"):
                st.warning("Please select a day!")
            else:
                with st.spinner('Loading...'):
                    header = {}
                    header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                    response = requests.request("GET", f"{API_URL}/database/goes18/prod/year/day?day={day_box}&year={year_box}&product={product_box}", headers=header)  #call to relevant fastapi endpoint
                    
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    hour_list = json_data   #store response data
                elif response.status_code == 401:   #when token is not authorized
                    st.error("Session token expired, please login again")   #display error
                    
                    st.stop()
                else:
                    st.error("Incorrect input given, please change")
                #define hour box
                hour_box = st.selectbox("Hour of the day for which you want data: ", ["--"]+hour_list, key='selected_hour')
                if (hour_box == "--"):
                    st.warning("Please select an hour!")
                else:
                    #display selections
                    st.write("Current selections, Product: ", product_box, ", Year: ", year_box, ", Day: ", day_box, ", Hour: ", hour_box)
                    #execute function with spinner
                    with st.spinner("Loading..."):
                        header = {}
                        header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                        response = requests.request("GET", f"{API_URL}/s3/goes18?year={year_box}&day={day_box}&hour={hour_box}&product={product_box}", headers=header)  #call to relevant fastapi endpoint
                        
                    if response.status_code == 200:
                        json_data = json.loads(response.text)
                        files_in_selected_hour = json_data  #store response data
                    elif response.status_code == 401:   #when token is not authorized
                        st.error("Session token expired, please login again")   #display error
                        
                        st.stop()
                    else:
                        st.error("Incorrect input given, please change")

                    #list available files at selected location
                    file_box = st.selectbox("Select a file: ", files_in_selected_hour, key='selected_file')
                    if (st.button("Download file")):
                        with st.spinner("Loading..."):
                            header = {}
                            header['Authorization'] = f"Bearer {st.session_state['access_token']}" #to verify token validity with JWT
                            response = requests.request("POST", f"{API_URL}/s3/goes18/copyfile?file_name={file_box}&product={product_box}&year={year_box}&day={day_box}&hour={hour_box}", headers=header)  #copy the selected file into user bucket with authorization
                            
                        if response.status_code == 200:
                            json_data = json.loads(response.text)
                            download_url = json_data    #store response data
                            st.success("File available for download.")      #display success message
                            st.write("URL to download file:", download_url)     #provide download URL
                        elif response.status_code == 401:   #when token is not authorized
                            st.error("Session token expired, please login again")   #display error
                            
                            st.stop()
                        else:
                            st.error("Incorrect input given, please change")
  
    #search by filename
    if (download_option == "Search by filename"):
        #filename text box
        
        filename_entered = st.text_input("Enter the filename")
        #fetch URL while calling spinner element
        with st.spinner("Loading..."):
            header = {}
            header['Authorization'] = f"Bearer {st.session_state['access_token']}" 
            response = requests.request("POST", f"{API_URL}/fetchfile/goes18?file_name={filename_entered}", headers=header)    #call to relevant fastapi endpoint with authorization
            
        if response.status_code == 404:
            have_limit_flag = False
            st.warning("No such file exists at GOES18 location")    #display no such file exists message
        elif response.status_code == 400:
            have_limit_flag = False
            st.error("Invalid filename format for GOES18")      #display invalid filename message
        elif response.status_code == 401:   #when token is not authorized
            st.error("Session token expired, please login again")   #display error
            
            st.stop()
        else:
            have_limit_flag = False
            with st.spinner("Loading..."): #spinner element
                header = {}
                header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                user_plan_response = requests.request("GET", f"{API_URL}/user/details?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
            if user_plan_response.status_code == 200:
                user_plan_resp = json.loads(user_plan_response.text)
                try:
                    api_calls = requests.request("GET", f"{API_URL}/logs/latest?username={st.session_state['username']}", headers=header)
                except:
                    st.error("Service unavailable, please try again later") #in case the API is not running
                    st.stop()   #stop the application   
                if api_calls.status_code == 200:
                    latest_logs_resp = json.loads(api_calls.text)   #store log responses from api
                    api_calls_in_last_hour = len(latest_logs_resp['timestamp']) #set values from log response api
                    
                    if (user_plan_resp == ["Free"]):
                        if (int(api_calls_in_last_hour) >= 10):
                            
                            st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                            st.write("Do you wish to upgrade?")
                            if (st.button("Yes")):
                                #call api for upgrading user plan
                                limit_chk = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                                if limit_chk.status_code == 200:
                                    st.success("Plan upgraded, please continue.")    #display success message
                                    #refresh app
                                    with st.spinner("Loading..."): 
                                        st.experimental_rerun()
                            if (st.button("No")):
                                st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                                st.experimental_rerun()

                        else:   #if hourly plan limit not exhausted
                            have_limit_flag = True
        
                    elif (user_plan_resp == ["Gold"]):
                        if (int(api_calls_in_last_hour) >= 15):
                            st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                            st.write("Do you wish to upgrade?")
                            if (st.button("Yes")):
                                #call api for upgrading user plan
                                limit_chk2 = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                                if limit_chk2.status_code == 200:
                                    st.success("Plan upgraded, please continue.")    #display success message
                                    #refresh app
                                    with st.spinner("Loading..."): 
                                        st.experimental_rerun()
                            if (st.button("No")):
                                st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                                st.experimental_rerun()

                        else:   #if hourly plan limit not exhausted
                            have_limit_flag = True
            
                    elif (user_plan_resp == ['Platinum']):
                        have_limit_flag = True
            
                    else:   #then admin user
                        have_limit_flag = True
        if (have_limit_flag):   
            json_data = json.loads(response.text)
            final_url = json_data   #store reponse data
            st.success("Found URL of the file available on GOES bucket!")     #display success message
            st.write("URL to file: ", final_url)
        
def nexrad_main():

    """Function called when NEXRAD page opened from streamlit application UI. Allows user to select action 
    they wish to perform: search and download NEXRAD files by fields or search for URL by filename.
    -----
    Input parameters:
    None
    -----
    Returns:
    Nothing
    """

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-03",
        logStreamName = "ui",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "User opened NEXRAD page"
            }
        ]
    )
    st.title("NEXRAD Radar File Downloader")
    st.markdown(
        """
        <style>
            .title {
                text-align: center;
                color: #2F80ED;
            }
        </style>
        <h2 class="title">Find the latest NEXRAD Radar Data</h2>
        <p></p>
        """,
        unsafe_allow_html=True,
    )

    #search options
    download_option = st.sidebar.radio ("Use following to search for NEXRAD radar data:",['Search by entering fields', 'Search by filename'])

    #search by fields
    if (download_option == "Search by entering fields"):
        st.write("Select all options in this form to download ")
        #bring in metadata from database to populate fields
        header = {}
        header['Authorization'] = f"Bearer {st.session_state['access_token']}"
        response = requests.request("GET", f"{API_URL}/database/nexrad", headers=header) #call to relevant fastapi endpoint
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-03",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/nexrad endpoint"
                        }
                    ]
                )
        if response.status_code == 200:
            have_limit_flag = False
            with st.spinner("Loading..."): #spinner element
                header = {}
                header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                user_plan_response = requests.request("GET", f"{API_URL}/user/details?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
            if user_plan_response.status_code == 200:
                user_plan_resp = json.loads(user_plan_response.text)
                try:
                    api_calls = requests.request("GET", f"{API_URL}/logs/latest?username={st.session_state['username']}", headers=header)
                except:
                    st.error("Service unavailable, please try again later") #in case the API is not running
                    st.stop()   #stop the application   
                if api_calls.status_code == 200:
                    latest_logs_resp = json.loads(api_calls.text)   #store log responses from api
                    api_calls_in_last_hour = len(latest_logs_resp['timestamp']) #set values from log response api
                    
                    if (user_plan_resp == ["Free"]):
                        if (int(api_calls_in_last_hour) >= 10):
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "ui",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "User shown hourly API limit exhausted page"
                                        }
                                    ]
                            )
                            st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                            st.write("Do you wish to upgrade?")
                            if (st.button("Yes")):
                                #call api for upgrading user plan
                                limit_chk = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "api",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "API endpoint: /user/updateplan\n Called by: " + st.session_state['username'] + " \n Response: 200 \nPlan upgraded successfully"
                                        }
                                    ]
                                )
                                if limit_chk.status_code == 200:
                                    st.success("Plan upgraded, please continue.")    #display success message
                                    #refresh app
                                    with st.spinner("Loading..."): 
                                        st.experimental_rerun()
                            if (st.button("No")):
                                st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                                st.experimental_rerun()

                        else:   #if hourly plan limit not exhausted
                            have_limit_flag = True
        
                    elif (user_plan_resp == ["Gold"]):
                        if (int(api_calls_in_last_hour) >= 15):
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "ui",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "User shown hourly API limit exhausted page"
                                        }
                                    ]
                            )
                            st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                            st.write("Do you wish to upgrade?")
                            if (st.button("Yes")):
                                #call api for upgrading user plan
                                limit_chk2 = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "api",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "API endpoint: /user/updateplan\n Called by: " + st.session_state['username'] + " \n Response: 200 \nPlan upgraded successfully"
                                        }
                                    ]
                                )
                                if limit_chk2.status_code == 200:
                                    st.success("Plan upgraded, please continue.")    #display success message
                                    #refresh app
                                    with st.spinner("Loading..."): 
                                        st.experimental_rerun()
                            if (st.button("No")):
                                st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                                st.experimental_rerun()

                        else:   #if hourly plan limit not exhausted
                            have_limit_flag = True
            
                    elif (user_plan_resp == ['Platinum']):
                        have_limit_flag = True
            
                    else:   #then admin user
                        have_limit_flag = True
        
        elif response.status_code == 401:   #when token is not authorized
            st.error("Session token expired, please login again")   #display error
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                logGroupName = "assignment-03",
                logStreamName = "api",
                logEvents = [
                    {
                    'timestamp' : int(time.time() * 1e3),
                    'message' : "API endpoint: /database/nexrad\n Called by: " + st.session_state['username'] + " \n Response: 401 \nSession token expired"
                    }
                ]
            )
            st.stop()
        else:  #incase the above line generated an exception due to database error
            st.error("Database not populated. Please come back later!") #show error message to populate database first
            st.stop()

        if (have_limit_flag):
            json_data = json.loads(response.text)
            years_in_nexrad = json_data #store reponse data

        else:
            st.stop()   #do not go any further

        #define year box
        year_box = st.selectbox("Year for which you are looking to get data for: ", ["--"]+years_in_nexrad, key="selected_year")
        if (year_box == "--"):
            st.warning("Please select an year!")
        else:
            with st.spinner("Loading..."):
                header = {}
                header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                response = requests.request("GET", f"{API_URL}/database/nexrad/year?year={year_box}", headers=header)   #call to relevant fastapi endpoint
                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-03",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/nexrad/year endpoint"
                        }
                    ]
                )
            if response.status_code == 200:
                json_data = json.loads(response.text)
                months_in_selected_year = json_data #store reponse data
            elif response.status_code == 401:   #when token is not authorized
                st.error("Session token expired, please login again")   #display error
                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-03",
                    logStreamName = "api",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "API endpoint: /database/nexrad/year\n Called by: " + st.session_state['username'] + " \n Response: 401 \nSession token expired"
                        }
                    ]
                )
                st.stop()
            else:
                st.error("Incorrect input given, please change")
            #months_in_selected_year = query_metadata_database.get_months_in_year_nexrad(year_box)   #months in selected year 
            #define day box
            month_box = st.selectbox("Month for which you are looking to get data for: ", ["--"]+months_in_selected_year, key="selected_month")
            if (month_box == "--"):
                st.warning("Please select month!")
            else:
                #days_in_selected_month = query_metadata_database.get_days_in_month_nexrad(month_box, year_box)  #days in selected year
                #define day box
                with st.spinner("Loading..."):
                    header = {}
                    header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                    response = requests.request("GET", f"{API_URL}/database/nexrad/year/month?month={month_box}&year={year_box}", headers=header)   #call to relevant fastapi endpoint
                    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-03",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/nexrad/year/month endpoint"
                        }
                    ]
                )
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    days_in_selected_month = json_data  #store reponse data
                elif response.status_code == 401:   #when token is not authorized
                    st.error("Session token expired, please login again")   #display error
                    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                        logGroupName = "assignment-03",
                        logStreamName = "api",
                        logEvents = [
                            {
                            'timestamp' : int(time.time() * 1e3),
                            'message' : "API endpoint: /database/nexrad/year/month\n Called by: " + st.session_state['username'] + " \n Response: 401 \nSession token expired"
                            }
                        ]
                    )
                    st.stop()
                else:
                    st.error("Incorrect input given, please change")
                day_box = st.selectbox("Day within year for which you want data: ", ["--"]+days_in_selected_month, key="selected_day")
                if (day_box == "--"):
                    st.warning("Please select a day!")
                else:
                    #ground_stations_in_selected_day = query_metadata_database.get_stations_for_day_nexrad(day_box, month_box, year_box)     #ground station in selected day     
                    #define ground station box
                    with st.spinner("Loading..."):
                        header = {}
                        header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                        response = requests.request("GET", f"{API_URL}/database/nexrad/year/month/day?day={day_box}&month={month_box}&year={year_box}", headers=header) #call to relevant fastapi endpoint
                        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                            logGroupName = "assignment-03",
                            logStreamName = "ui",
                            logEvents = [
                                {
                                'timestamp' : int(time.time() * 1e3),
                                'message' : "User called /database/nexrad/year/month/day endpoint"
                                }
                            ]
                        )
                    if response.status_code == 200:
                        json_data = json.loads(response.text)
                        ground_stations_in_selected_day = json_data #store reponse data
                    elif response.status_code == 401:   #when token is not authorized
                        st.error("Session token expired, please login again")   #display error
                        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                            logGroupName = "assignment-03",
                            logStreamName = "api",
                            logEvents = [
                                {
                                'timestamp' : int(time.time() * 1e3),
                                'message' : "API endpoint: /database/nexrad/year/month/day\n Called by: " + st.session_state['username'] + " \n Response: 401 \nSession token expired"
                                }
                            ]
                        )
                        st.stop()
                    else:
                        st.error("Incorrect input given, please change")
                    
                    ground_station_box = st.selectbox("Station for which you want data: ", ["--"]+ground_stations_in_selected_day, key='selected_ground_station')
                    if (ground_station_box == "--"):
                        st.warning("Please select a station!")
                    else: 
                        #display selections
                        st.write("Current selections, Year: ", year_box, ", Month: ", month_box, ", Day: ", day_box, ", Station: ", ground_station_box)

                        #execute function with spinner
                        with st.spinner("Loading..."):
                            header = {}
                            header['Authorization'] = f"Bearer {st.session_state['access_token']}"    #list file names for given selection
                            response = requests.request("GET", f"{API_URL}/s3/nexrad?year={year_box}&month={month_box}&day={day_box}&ground_station={ground_station_box}", headers=header)  #call to relevant fastapi endpoint
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                logGroupName = "assignment-03",
                                logStreamName = "ui",
                                logEvents = [
                                    {
                                    'timestamp' : int(time.time() * 1e3),
                                    'message' : "User called /s3/nexrad endpoint to get file list"
                                    }
                                ]
                            )
                        if response.status_code == 200:
                            json_data = json.loads(response.text)
                            files_in_selected_station = json_data   #store reponse data
                        elif response.status_code == 401:   #when token is not authorized
                            st.error("Session token expired, please login again")   #display error
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                logGroupName = "assignment-03",
                                logStreamName = "api",
                                logEvents = [
                                    {
                                    'timestamp' : int(time.time() * 1e3),
                                    'message' : "API endpoint: /s3/nexrad\n Called by: " + st.session_state['username'] + " \n Response: 401 \nSession token expired"
                                    }
                                ]
                            )
                            st.stop()
                        else:
                            st.error("Incorrect input given, please change")

                        file_box = st.selectbox("Select a file: ", files_in_selected_station, key='selected_file')
                        if (st.button("Download file")):
                            with st.spinner("Loading..."):
                                header = {}
                                header['Authorization'] = f"Bearer {st.session_state['access_token']}" 
                                response = requests.request("POST", f"{API_URL}/s3/nexrad/copyfile?file_name={file_box}&year={year_box}&month={month_box}&day={day_box}&ground_station={ground_station_box}", headers=header)  #call to relevant fastapi endpoint with authorization
                                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "ui",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "User called /s3/nexrad/copyfile endpoint to copy/download file"
                                        }
                                    ]
                                )
                            if response.status_code == 200:
                                json_data = json.loads(response.text)
                                download_url = json_data    #store reponse data
                                st.success("File available for download.")      #display success message
                                st.write("URL to download file:", download_url)     #provide download URL
                            elif response.status_code == 401:   #when token is not authorized
                                st.error("Session token expired, please login again")   #display error
                                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "api",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "API endpoint: /s3/nexrad/copyfile\n Called by: " + st.session_state['username'] + " \n Response: 401 \nSession token expired"
                                        }
                                    ]
                                )
                                st.stop()
                            else:
                                st.error("Incorrect input given, please change")

    #search by filename
    if download_option == "Search by filename":
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-03",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called NEXRAD - Search by filename page"
                        }
                    ]
                )
        #filename text box
        filename_entered = st.text_input("Enter the filename")
        #fetch URL while calling spinner element
        with st.spinner("Loading..."):
            header = {}
            header['Authorization'] = f"Bearer {st.session_state['access_token']}" 
            response = requests.request("POST", f"{API_URL}/fetchfile/nexrad?file_name={filename_entered}", headers=header)    #call to relevant fastapi endpoint with authorization
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-03",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /fetchfile/nexrad endpoint for get file url"
                        }
                    ]
                )
        if response.status_code == 404:
            have_limit_flag = False
            st.warning("No such file exists at NEXRAD location")    #display no such file exists message
        elif response.status_code == 401:   #when token is not authorized
            st.error("Session token expired, please login again")   #display error
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                logGroupName = "assignment-03",
                logStreamName = "api",
                logEvents = [
                    {
                    'timestamp' : int(time.time() * 1e3),
                    'message' : "API endpoint: /fetchfile/nexrad\n Called by: " + st.session_state['username'] + " \n Response: 401 \nSession token expired"
                    }
                ]
            )
            st.stop()
        elif response.status_code == 400:
            have_limit_flag = False
            st.error("Invalid filename format for NEXRAD")      #display invalid filename message
        else:
            have_limit_flag = False
            with st.spinner("Loading..."): #spinner element
                header = {}
                header['Authorization'] = f"Bearer {st.session_state['access_token']}"
                user_plan_response = requests.request("GET", f"{API_URL}/user/details?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
            if user_plan_response.status_code == 200:
                user_plan_resp = json.loads(user_plan_response.text)
                try:
                    api_calls = requests.request("GET", f"{API_URL}/logs/latest?username={st.session_state['username']}", headers=header)
                except:
                    st.error("Service unavailable, please try again later") #in case the API is not running
                    st.stop()   #stop the application   
                if api_calls.status_code == 200:
                    latest_logs_resp = json.loads(api_calls.text)   #store log responses from api
                    api_calls_in_last_hour = len(latest_logs_resp['timestamp']) #set values from log response api
                    
                    if (user_plan_resp == ["Free"]):
                        if (int(api_calls_in_last_hour) >= 10):
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "ui",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "User shown hourly API limit exhausted page"
                                        }
                                    ]
                            )
                            st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                            st.write("Do you wish to upgrade?")
                            if (st.button("Yes")):
                                #call api for upgrading user plan
                                limit_chk = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "api",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "API endpoint: /user/updateplan\n Called by: " + st.session_state['username'] + " \n Response: 200 \nPlan upgraded successfully"
                                        }
                                    ]
                                )
                                if limit_chk.status_code == 200:
                                    st.success("Plan upgraded, please continue.")    #display success message
                                    #refresh app
                                    with st.spinner("Loading..."): 
                                        st.experimental_rerun()
                            if (st.button("No")):
                                st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                                st.experimental_rerun()

                        else:   #if hourly plan limit not exhausted
                            have_limit_flag = True
        
                    elif (user_plan_resp == ["Gold"]):
                        if (int(api_calls_in_last_hour) >= 15):
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "ui",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "User shown hourly API limit exhausted page"
                                        }
                                    ]
                            )
                            st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                            st.write("Do you wish to upgrade?")
                            if (st.button("Yes")):
                                #call api for upgrading user plan
                                limit_chk2 = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-03",
                                    logStreamName = "api",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "API endpoint: /user/updateplan\n Called by: " + st.session_state['username'] + " \n Response: 200 \nPlan upgraded successfully"
                                        }
                                    ]
                                )
                                if limit_chk2.status_code == 200:
                                    st.success("Plan upgraded, please continue.")    #display success message
                                    #refresh app
                                    with st.spinner("Loading..."): 
                                        st.experimental_rerun()
                            if (st.button("No")):
                                st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                                st.experimental_rerun()

                        else:   #if hourly plan limit not exhausted
                            have_limit_flag = True
            
                    elif (user_plan_resp == ['Platinum']):
                        have_limit_flag = True
            
                    else:   #then admin user
                        have_limit_flag = True
        if (have_limit_flag):       
            json_data = json.loads(response.text)
            final_url = json_data   #store reponse data
            st.success("Found URL of the file available on NEXRAD bucket!")     #display success message
            st.write("URL to file: ", final_url)

def map_main():

    """Function called when NEXRAD Locations - Map page opened from streamlit application UI. Displays plot of NEXRAD satellite
    locations in the USA after reading data from the corresponding SQLite table.
    -----
    Input parameters:
    None
    -----
    Returns:
    Nothing
    """

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-03",
        logStreamName = "ui",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "User opened NEXRAD Locations - Map page"
            }
        ]
    )
    st.markdown(
        """
        <h1 style="background-color:#1c1c1c; color: white; text-align: center; padding: 15px; border-radius: 10px">
            Map Page
        </h1>
        """,
        unsafe_allow_html=True,
    )
    
    with st.spinner("Loading..."):
        header = {}
        header['Authorization'] = f"Bearer {st.session_state['access_token']}"
        response = requests.request("GET", f"{API_URL}/database/mapdata", headers=header)  #call to relevant fastapi endpoint with authorization
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-03",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/mapdata endpoint"
                        }
                    ]
                )
    if response.status_code == 404:
        st.warning("Unable to fetch mapdata")    #incase the above line generated an exception due to database error
        st.stop()
    elif response.status_code == 401: #when token is not authorized
        st.error("Session token expired, please login again")   #display error
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-03",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "API endpoint: /database/mapdata\n Called by: " + st.session_state['username'] + " \n Response: 401 \nSession token expired"
                }
            ]
        )
        st.stop()
    elif response.status_code == 200:
        have_limit_flag = False
        with st.spinner("Loading..."): #spinner element
            header = {}
            header['Authorization'] = f"Bearer {st.session_state['access_token']}"
            user_plan_response = requests.request("GET", f"{API_URL}/user/details?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
        if user_plan_response.status_code == 200:
            user_plan_resp = json.loads(user_plan_response.text)
            try:
                api_calls = requests.request("GET", f"{API_URL}/logs/latest?username={st.session_state['username']}", headers=header)
            except:
                st.error("Service unavailable, please try again later") #in case the API is not running
                st.stop()   #stop the application   
            if api_calls.status_code == 200:
                latest_logs_resp = json.loads(api_calls.text)   #store log responses from api
                api_calls_in_last_hour = len(latest_logs_resp['timestamp']) #set values from log response api
                
                if (user_plan_resp == ["Free"]):
                    if (int(api_calls_in_last_hour) >= 10):
                        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                logGroupName = "assignment-03",
                                logStreamName = "ui",
                                logEvents = [
                                    {
                                    'timestamp' : int(time.time() * 1e3),
                                    'message' : "User shown hourly API limit exhausted page"
                                    }
                                ]
                        )
                        st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                        st.write("Do you wish to upgrade?")
                        if (st.button("Yes")):
                            #call api for upgrading user plan
                            limit_chk = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                logGroupName = "assignment-03",
                                logStreamName = "api",
                                logEvents = [
                                    {
                                    'timestamp' : int(time.time() * 1e3),
                                    'message' : "API endpoint: /user/updateplan\n Called by: " + st.session_state['username'] + " \n Response: 200 \nPlan upgraded successfully"
                                    }
                                ]
                            )
                            if limit_chk.status_code == 200:
                                st.success("Plan upgraded, please continue.")    #display success message
                                #refresh app
                                with st.spinner("Loading..."): 
                                    st.experimental_rerun()
                        if (st.button("No")):
                            st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                            st.experimental_rerun()

                    else:   #if hourly plan limit not exhausted
                        have_limit_flag = True
       
                elif (user_plan_resp == ["Gold"]):
                    if (int(api_calls_in_last_hour) >= 15):
                        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                logGroupName = "assignment-03",
                                logStreamName = "ui",
                                logEvents = [
                                    {
                                    'timestamp' : int(time.time() * 1e3),
                                    'message' : "User shown hourly API limit exhausted page"
                                    }
                                ]
                        )
                        st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                        st.write("Do you wish to upgrade?")
                        if (st.button("Yes")):
                            #call api for upgrading user plan
                            limit_chk2 = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                logGroupName = "assignment-03",
                                logStreamName = "api",
                                logEvents = [
                                    {
                                    'timestamp' : int(time.time() * 1e3),
                                    'message' : "API endpoint: /user/updateplan\n Called by: " + st.session_state['username'] + " \n Response: 200 \nPlan upgraded successfully"
                                    }
                                ]
                            )
                            if limit_chk2.status_code == 200:
                                st.success("Plan upgraded, please continue.")    #display success message
                                #refresh app
                                with st.spinner("Loading..."): 
                                    st.experimental_rerun()
                        if (st.button("No")):
                            st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                            st.experimental_rerun()

                    else:   #if hourly plan limit not exhausted
                        have_limit_flag = True
         
                elif (user_plan_resp == ['Platinum']):
                    have_limit_flag = True
         
                else:   #then admin user
                    have_limit_flag = True

    else:
        st.error("Database not populated. Please come back later!") #else database not populated, show error message to populate database first
        st.stop()

    if (have_limit_flag):
        json_data = json.loads(response.text)
        map_dict = json_data
        #plotting the coordinates extracted on a map
        hover_text = []
        for j in range(len(map_dict)):      #building the text to display when hovering over each point on the plot
            hover_text.append("Station: " + map_dict['stations'][j] + " County:" + map_dict['counties'][j] + ", " + map_dict['states'][j])

        #use plotly to plot
        map_fig = go.Figure(data=go.Scattergeo(
                lon = map_dict['longitude'],
                lat = map_dict['latitude'],
                text = hover_text,
                marker= {
                    "color": map_dict['elevation'],
                    "colorscale": "Viridis",
                    "colorbar": {
                        "title": "Elevation"
                    },
                    "size": 14,
                    "symbol": "circle",
                    "line" : {
                        "color": 'black',
                        "width": 1
                    }
                }
            ))

        #plot layout
        map_fig.update_layout(
                title = 'All NEXRAD satellite locations along with their elevations',
                geo_scope='usa',
                mapbox = {
                        "zoom": 12,
                        "pitch": 0,
                        "center": {
                            "lat": 31.0127195,
                            "lon": 121.413115
                        }
                },
                font = {
                    "size": 18
                },
                autosize= True
            )

        map_fig.update_layout(height=700)
        st.plotly_chart(map_fig, use_container_width=True, height=700)     #plotting on streamlit page

## Main functionality begins here 

#img = Image.open('radar-icon.png')  #for icon of the streamlit wwebsite tab
st.set_page_config(page_title="Weather Data Files", layout="wide")

if 'if_logged' not in st.session_state:
    st.session_state['if_logged'] = False
    st.session_state['access_token'] = ''
    st.session_state['username'] = ''

if st.session_state['if_logged'] == True:
    col1, col2, col3 , col4, col5 = st.columns(5)

    with col1:
        header = {}
        header['Authorization'] = f"Bearer {st.session_state['access_token']}"
        response = requests.request("GET", f"{API_URL}/user/details?username={st.session_state['username']}", headers=header)  #call to relevant fastapi endpoint with authorization
        if response.status_code == 200:
            curr_user_plan = json.loads(response.text)
            st.write("Your plan: ", curr_user_plan[0])
        else:
            pass
    with col2:
        pass
    with col3 :
        pass
    with col4:
        pass
    with col5:
        logout_button = st.button(label='Logout', disabled=False)

    if logout_button:
        st.session_state['if_logged'] = False
        st.experimental_rerun()

if st.session_state['if_logged'] == False:
    login_or_signup = st.selectbox("Please select an option", ["Login", "Signup", "Forgot password?"])

    if login_or_signup=="Login":
        st.write("Enter your credentials to login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == '' or password == '':
                st.warning("Please enter both username and password.")
            else:
                with st.spinner("Wait.."):
                    payload = {'username': username, 'password': password}
                    try:
                        response = requests.request("POST", f"{API_URL}/login", data=payload)
                        
                    except:
                        st.error("Service unavailable, please try again later") #in case the API is not running
                        st.stop()   #stop the application
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    st.session_state['if_logged'] = True
                    st.session_state['access_token'] = json_data['access_token']
                    st.session_state['username'] = username
                    st.success("Login successful")
                    st.experimental_rerun()
                else:
                    st.error("Incorrect username or password.")

    elif login_or_signup=="Signup":
        st.write("Create an account to get started")
        name = st.text_input("Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        #ddd the plan selection field
        plans = [
        {
        'name': 'Free',
        'details': '10 API requests hourly'
        },
        {
        'name': 'Gold',
        'details': '15 API requests hourly'
        },
        {
        'name': 'Platinum',
        'details': 'Unlimited API requests hourly'
        }
        ]

        selected_plan = st.selectbox('Select a plan', [f"{plan['name']} - {plan['details']}" for plan in plans])    #choose api plan  

        if st.button("Signup"):
            if len(password) < 4:
                st.warning("Password should be of 4 characters minimum")
            elif name == '' or username == '' or password == '' or confirm_password == '':
                st.warning("Please fill in all the fields.")
            elif password != confirm_password:
                with st.spinner("Wait.."):
                    st.warning("Passwords do not match.")
            else:
                with st.spinner("Wait.."):
                    try:
                        selected_plan = selected_plan.split()   #split the returned list by spaces to just extract the plan name
                        user_type="User"    #default user type for all users created through app (admin users can only be created by developers)
                        payload = {'name': name, 'username': username, 'password': password, 'plan': selected_plan[0], 'user_type': user_type}
                        response = requests.request("POST", f"{API_URL}/user/create", json=payload)
                        
                    except:
                        st.error("Service unavailable, please try again later") #in case the API is not running
                        st.stop()   #stop the application
                if response.status_code == 200:
                    st.success("Account created successfully! Please login to continue.")
                elif response.status_code == 400:
                    st.error("Username already exists, please login")
                else:
                    st.error("Error creating account. Please try again.")

    elif login_or_signup=="Forgot password?":
        st.write("Enter your details to reset password")
        username2 = st.text_input("Enter username to reset password for")
        password2 = st.text_input("Enter new password", type="password")
        if st.button("Reset"):
            if username2 == '' or password2 == '':  #sanity check
                st.warning("Please enter both username and password.")
            elif len(password2) < 4:    #password length check
                st.warning("Password should be of 4 characters minimum")
            else:
                with st.spinner("Wait.."):
                    pass_payload = {'password': password2}
                    try:
                        response = requests.request("PATCH", f"{API_URL}/user/update?username={username2}", json=pass_payload)  #call to relevant fastapi endpoint with authorization
                    except:
                        st.error("Service unavailable, please try again later") #in case the API is not running
                        st.stop()   #stop the application
                if response.status_code == 200:
                    st.success("Reset password successful! Please login")   #success message
                elif response.status_code == 404:
                    st.warning("User not found, please check username")     #user does not exist
                else:
                    st.error("Something went wrong, try again later.")

if st.session_state['if_logged'] == True:
    page = st.sidebar.selectbox("Select a page", ["GOES-18", "NEXRAD", "NEXRAD Locations - Map", "Dashboards"])   #main options of streamlit app

    if page == "GOES-18":
        with st.spinner("Loading..."): #spinner element
            goes_main()
    elif page == "NEXRAD":
        with st.spinner("Loading..."): #spinner element
            nexrad_main()
    elif page == "NEXRAD Locations - Map":
        with st.spinner("Generating map..."): #spinner element
            map_main()
    elif page == "Dashboards":
        with st.spinner("Loading..."): #spinner element
            header = {}
            header['Authorization'] = f"Bearer {st.session_state['access_token']}"
            response = requests.request("GET", f"{API_URL}/user/details?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
        if response.status_code == 200:
            user_plan_resp = json.loads(response.text)
            try:
                api_calls = requests.request("GET", f"{API_URL}/logs/latest?username={st.session_state['username']}", headers=header)
            except:
                st.error("Service unavailable, please try again later") #in case the API is not running
                st.stop()   #stop the application   
            if api_calls.status_code == 200:
                latest_logs_resp = json.loads(api_calls.text)   #store log responses from api
                api_calls_in_last_hour = len(latest_logs_resp['timestamp']) #set values from log response api
                
                if (user_plan_resp == ["Free"]):
                    if (int(api_calls_in_last_hour) >= 10):
                        
                        st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                        st.write("Do you wish to upgrade?")
                        if (st.button("Yes")):
                            #call api for upgrading user plan
                            limit_chk = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                            
                            if limit_chk.status_code == 200:
                                st.success("Plan upgraded, please continue.")    #display success message
                                #refresh app
                                with st.spinner("Loading..."): 
                                    st.experimental_rerun()
                        if (st.button("No")):
                            st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                            st.experimental_rerun()

                    else:   #if hourly plan limit not exhausted
                        with st.spinner("Loading..."): #spinner element
                            dashboard_user_main()   #continue to perform what user originally called for 
                
                elif (user_plan_resp == ["Gold"]):
                    if (int(api_calls_in_last_hour) >= 15):
                        
                        st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                        st.write("Do you wish to upgrade?")
                        if (st.button("Yes")):
                            #call api for upgrading user plan
                            limit_chk2 = requests.request("POST", f"{API_URL}/user/updateplan?username={st.session_state['username']}", headers=header)  #get user type by call to relevant fastapi endpoint with authorization
                            
                            if limit_chk2.status_code == 200:
                                st.success("Plan upgraded, please continue.")    #display success message
                                #refresh app
                                with st.spinner("Loading..."): 
                                    st.experimental_rerun()
                        if (st.button("No")):
                            st.session_state['if_logged'] = False   #if plan not upgraded, logout user
                            st.experimental_rerun()

                    else:   #if hourly plan limit not exhausted
                        with st.spinner("Loading..."): #spinner element
                            dashboard_user_main()   #continue to perform what user originally called for 
                
                elif (user_plan_resp == ['Platinum']):
                    #####replace always with what needs to be done on successful api call & when use has call limit left
                    with st.spinner("Loading..."): 
                        dashboard_user_main()   #continue to perform what user originally called for 
                
                else:   #then admin user
                    with st.spinner("Loading..."): #spinner element
                        #call admin dashboard
                        dashboard_admin_main()  #continue to perform what user originally called for
            
        else:
            st.error("Session token expired, please login again")   #display error
            st.stop()