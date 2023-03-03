import os
import time
import json
import boto3
import requests
from PIL import Image
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path('./.env')
load_dotenv(dotenv_path)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['access_token'] = ''
    st.session_state['username'] = ''

BASE_URL = "http://localhost:8001"

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

with st.sidebar:
    if st.session_state and st.session_state.logged_in and st.session_state.username:
        st.write(f'Current User: {st.session_state.username}')
    else:
        st.write('Current User: Not Logged In')
    
    response = requests.get(f"{BASE_URL}/user/details?username={st.session_state.username}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
    if response.status_code == 200:
        user_plan = json.loads(response.text)
        st.write("Your plan: ", user_plan[0])
    
    logout_button = st.button('Log Out')
    if logout_button:
        st.session_state['logged_in'] = False
        st.experimental_rerun()

if st.session_state['logged_in'] == True:
    st.markdown("<h2 style='text-align: center;'>Data Exploration of the GEOS dataset 🌎</h1>", unsafe_allow_html=True)
    st.header("")
    st.image(Image.open('../streamlit/pages/Satellite-data-for-imagery.jpeg'))
    
    option = st.selectbox('Select the option to search file', ('Select Search Type', 'Search By Field 🔎', 'Search By Filename 🔎'))
    
    if option == 'Select Search Type':
        st.error('Select an input field')
    
    elif option == 'Search By Field 🔎':
        with st.spinner('Wait for it...'):
            st.markdown("<h3 style='text-align: center;'>Search Through Fields 🔎</h1>", unsafe_allow_html=True)
            response = requests.get(f"{BASE_URL}/noaa-database/goes18", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
            if response.status_code == 200:
                api_limit_flag = False
                with st.spinner('Wait for it...'):
                    user_plan_response = requests.get(f"{BASE_URL}/user/user-details?username={st.session_state.username}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                if user_plan_response.status_code == 200:
                    user_plan_data = json.loads(user_plan_response.text)
                    try:
                        api_calls = requests.get(f"{BASE_URL}/user/logs/latest?username={st.session_state.username}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                    except:
                        st.error("Service unavailable, please try again later")
                        st.stop()
                    if api_calls.status_code == 200:
                        latest_logs_resp = json.loads(api_calls.text)
                        api_calls_in_last_hour = len(latest_logs_resp['timestamp'])
                        
                        if user_plan_data == ["Free"]:
                            if int(api_calls_in_last_hour) >= 10:
                                st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                                st.write("Do you wish to upgrade?")
                                if st.button("Yes"):
                                    check_limit = requests.post(f"{BASE_URL}/user/upgradeplan?username={st.session_state.username}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                                    write_logs("API endpoint: /user/upgradeplan\n Called by: " + st.session_state.username + " \n Response: 200 \nPlan upgraded successfully")
                                    if check_limit.status_code == 200:
                                        st.success("Plan upgraded, please continue.")
                                        with st.spinner("Loading..."): 
                                            st.experimental_rerun()
                                if st.button("No"):
                                    st.session_state['logged_in'] = False
                                    st.experimental_rerun()
                            else:
                                api_limit_flag = True

                        elif user_plan_data == ["Gold"]:
                            if int(api_calls_in_last_hour) >= 15:
                                st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                                st.write("Do you wish to upgrade?")
                                if st.button("Yes"):
                                    check_limit_2 = requests.post(f"{BASE_URL}/user/upgradeplan?username={st.session_state.username}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                                    write_logs("API endpoint: /user/upgradeplan\n Called by: " + st.session_state.username + " \n Response: 200 \nPlan upgraded successfully")
                                    if check_limit_2.status_code == 200:
                                        st.success("Plan upgraded, please continue.")
                                        with st.spinner("Loading..."): 
                                            st.experimental_rerun()
                                if st.button("No"):
                                    st.session_state['logged_in'] = False
                                    st.experimental_rerun()
                            else:
                                api_limit_flag = True

                        elif user_plan_data == ['Platinum']:
                            api_limit_flag = True

                        else:
                            api_limit_flag = True
            elif response.status_code == 401:
                st.error("Session token expired, please login again")
                write_logs("API endpoint: /noaa-database/goes18\n Called by: " + st.session_state.username + " \n Response: 401 \nSession token expired")
                st.stop()
            else:
                st.error("Database not populated. Please come back later!")
                st.stop()

            if api_limit_flag:
                json_data = json.loads(response.text)
                products = json_data
                write_logs("API endpoint: /noaa-database/goes18\n Called by: " + st.session_state.username + " \n Response: 200 \nSuccessfully updated Products")
            else:
                st.stop()

            product_input = st.selectbox("Product name: ", products, disabled = True, key="selected_product")
            with st.spinner('Loading...'):
                response = requests.get(f"{BASE_URL}/noaa-database/goes18/prod?product={product_input}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
            if response.status_code == 200:
                json_data = json.loads(response.text)
                years = json_data
                write_logs("API endpoint: /noaa-database/goes18/prod\n Called by: " + st.session_state.username + " \n Response: 200 \nSuccessfully updated Years")
            elif response.status_code == 401:
                st.error("Session token expired, please login again")
                write_logs("API endpoint: /noaa-database/goes18/prod\n Called by: " + st.session_state.username + " \n Response: 401 \nSession token expired")
                st.stop()
            else:
                st.error("Incorrect input given, please change")
                
            year_input = st.selectbox("Year for which you are looking to get data for: ", [" "] + years, key="selected_year")
            if (year_input == " "):
                st.warning("Please select a year!")
            else:
                with st.spinner('Loading...'):
                    response = requests.get(f"{BASE_URL}/noaa-database/goes18/prod/year?year={year_input}&product={product_input}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    days = json_data
                    write_logs("API endpoint: /noaa-database/goes18/prod/year\n Called by: " + st.session_state.username + " \n Response: 200 \nSuccessfully updated Days")
                elif response.status_code == 401:
                    st.error("Session token expired, please login again")
                    write_logs("API endpoint: /noaa-database/goes18/prod/year\n Called by: " + st.session_state.username + " \n Response: 401 \nSession token expired")
                    st.stop()
                else:
                    st.error("Incorrect input given, please change")

                day_input = st.selectbox("Day within year for which you want data: ", [" "] + days, key="selected_day")
                if (day_input == " "):
                    st.warning("Please select a day!")
                else:
                    with st.spinner('Loading...'):
                        response = requests.get(f"{BASE_URL}/noaa-database/goes18/prod/year/day?day={day_input}&year={year_input}&product={product_input}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                    if response.status_code == 200:
                        json_data = json.loads(response.text)
                        hours = json_data
                        write_logs("API endpoint: /noaa-database/goes18/prod/year/day\n Called by: " + st.session_state.username + " \n Response: 200 \nSuccessfully updated Hours")
                    elif response.status_code == 401:
                        st.error("Session token expired, please login again")
                        write_logs("API endpoint: /noaa-database/goes18/prod/year/day\n Called by: " + st.session_state.username + " \n Response: 401 \nSession token expired")
                        st.stop()
                    else:
                        st.error("Incorrect input given, please change")
                        
                    hour_input = st.selectbox("Hour of the day for which you want data: ", [" "] + hours, key='selected_hour')
                    if (hour_input == " "):
                        st.warning("Please select an hour!")
                    else:
                        with st.spinner("Loading..."):
                            response = requests.get(f"{BASE_URL}/aws-s3-files/goes18?year={year_input}&day={day_input}&hour={hour_input}&product={product_input}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                        if response.status_code == 200:
                            json_data = json.loads(response.text)
                            files_available = json_data
                            write_logs("API endpoint: /aws-s3-files/goes18\n Called by: " + st.session_state.username + " \n Response: 200 \nSuccessfully updated list of files")
                        elif response.status_code == 401:
                            st.error("Session token expired, please login again")
                            write_logs("API endpoint: /aws-s3-files/goes18\n Called by: " + st.session_state.username + " \n Response: 401 \nSession token expired")
                            st.stop()
                        else:
                            st.error("Incorrect input given, please change")

                        file_input = st.selectbox("Select a file: ", files_available, key='selected_file')
                        if st.button('Fetch file ©️'):
                            with st.spinner("Loading..."):
                                response = requests.post(f"{BASE_URL}/aws-s3-files/goes18/copyfile?file_name={file_input}&product={product_input}&year={year_input}&day={day_input}&hour={hour_input}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                            if response.status_code == 200:
                                json_data = json.loads(response.text)
                                download_url = json_data
                                st.success("File available for download.")
                                st.write("URL to download file:", download_url)
                                write_logs("API endpoint: /aws-s3-files/goes18/copyfile\n Called by: " + st.session_state.username + " \n Response: 200 \nSuccessfully downloaded file")
                            elif response.status_code == 401:
                                st.error("Session token expired, please login again")
                                write_logs("API endpoint: /aws-s3-files/goes18/copyfile\n Called by: " + st.session_state.username + " \n Response: 401 \nSession token expired")
                                st.stop()
                            else:
                                st.error("Incorrect input given, please change")
    
    elif option == 'Search By Filename 🔎':
        with st.spinner('Wait for it...'):
            st.markdown("<h3 style='text-align: center;'>Search Through Filename 🔎</h1>", unsafe_allow_html=True)
            file_name = st.text_input('NOAA GEOS-18 Filename',)
            if st.button('Fetch file ©️'):
                with st.spinner("Loading..."):
                    response = requests.post(f"{BASE_URL}/aws-s3-fetchfile/goes18?file_name={file_name}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                if response.status_code == 404:
                    api_limit_flag = False
                    st.warning("No such file exists at GOES18 location")
                elif response.status_code == 400:
                    api_limit_flag = False
                    st.error("Invalid filename format for GOES18")
                elif response.status_code == 401:
                    st.error("Session token expired, please login again")
                    write_logs("API endpoint: /aws-s3-fetchfile/goes18\n Called by: " + st.session_state.username + " \n Response: 401 \nSession token expired")
                    st.stop()
                else:
                    api_limit_flag = False
                    with st.spinner('Wait for it...'):
                        user_plan_response = requests.get(f"{BASE_URL}/user/user-details?username={st.session_state.username}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                    if user_plan_response.status_code == 200:
                        user_plan_data = json.loads(user_plan_response.text)
                        try:
                            api_calls = requests.get(f"{BASE_URL}/user/logs/latest?username={st.session_state.username}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                        except:
                            st.error("Service unavailable, please try again later")
                            st.stop()
                        if api_calls.status_code == 200:
                            latest_logs_resp = json.loads(api_calls.text)
                            api_calls_in_last_hour = len(latest_logs_resp['timestamp'])
                            
                            if user_plan_data == ["Free"]:
                                if int(api_calls_in_last_hour) >= 10:
                                    st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                                    st.write("Do you wish to upgrade?")
                                    if st.button("Yes"):
                                        check_limit = requests.post(f"{BASE_URL}/user/upgradeplan?username={st.session_state.username}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                                        write_logs("API endpoint: /user/upgradeplan\n Called by: " + st.session_state.username + " \n Response: 200 \nPlan upgraded successfully")
                                        if check_limit.status_code == 200:
                                            st.success("Plan upgraded, please continue.")
                                            with st.spinner("Loading..."): 
                                                st.experimental_rerun()
                                    if st.button("No"):
                                        st.session_state['logged_in'] = False
                                        st.experimental_rerun()
                                else:
                                    api_limit_flag = True

                            elif user_plan_data == ["Gold"]:
                                if int(api_calls_in_last_hour) >= 15:
                                    st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                                    st.write("Do you wish to upgrade?")
                                    if st.button("Yes"):
                                        check_limit_2 = requests.post(f"{BASE_URL}/user/upgradeplan?username={st.session_state.username}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                                        write_logs("API endpoint: /user/upgradeplan\n Called by: " + st.session_state.username + " \n Response: 200 \nPlan upgraded successfully")
                                        if check_limit_2.status_code == 200:
                                            st.success("Plan upgraded, please continue.")
                                            with st.spinner("Loading..."): 
                                                st.experimental_rerun()
                                    if st.button("No"):
                                        st.session_state['logged_in'] = False
                                        st.experimental_rerun()
                                else:
                                    api_limit_flag = True

                            elif user_plan_data == ['Platinum']:
                                api_limit_flag = True

                            else:
                                api_limit_flag = True

                if api_limit_flag:
                    json_data = json.loads(response.text)
                    final_url = json_data
                    write_logs("API endpoint: /aws-s3-fetchfile/goes18\n Called by: " + st.session_state.username + " \n Response: 200 \nSuccessfully downloaded file")
                    st.success("Found URL of the file available on GOES bucket!")
                    st.write("URL to file: ", final_url)

else:
    st.title("Please sign-in to access this feature!")