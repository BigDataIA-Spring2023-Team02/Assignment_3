import os
import time
import json
import boto3
import folium
import requests
import warnings
import streamlit as st
from pathlib import Path
import streamlit_folium as stf
from dotenv import load_dotenv

warnings.simplefilter(action='ignore', category=FutureWarning)
dotenv_path = Path('./.env')
load_dotenv(dotenv_path)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['access_token'] = ''
    st.session_state['username'] = ''

BASE_URL = "http://localhost:8000"

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
    st.markdown("<h2 style='text-align: center;'>NexRad Map Geo-Locations 📍</h1>", unsafe_allow_html=True)
    
    with st.spinner('Refreshing map locations ...'):
        
        response = requests.get(f"{BASE_URL}/noaa-database/mapdata", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
        if response.status_code == 404:
            st.warning("Unable to fetch mapdata")
            st.stop()
        elif response.status_code == 401:
            st.error("Session token expired, please login again")
            write_logs("API endpoint: /noaa-database/mapdata\n Called by: " + st.session_state.username + " \n Response: 401 \nSession token expired")
            st.stop()
        elif response.status_code == 200:
            write_logs("API endpoint: /noaa-database/mapdata\n Called by: " + st.session_state.username + " \n Response: 200 \nUploaded Map Data")
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
        else:
            st.error("Database not populated. Please come back later!")
            st.stop()
        if api_limit_flag:
            json_data = json.loads(response.text)
            map_dict = json_data
            map = folium.Map(location=[40,-100], tiles="OpenStreetMap", zoom_start=4)
            for i in range(len(map_dict["Station_Code"])):
                tooltip_text = f"Station Code: {map_dict['Station_Code'][i]}, County: {map_dict['County'][i]}"
                folium.Marker([map_dict["latitude"][i],map_dict["longitude"][i]],
                            tooltip = tooltip_text
                            ).add_to(map)

            st.markdown("<h2 style='text-align: center;'>Nexrad Station Pointers</h1>", unsafe_allow_html=True)
            stf.st_folium(map, width=700, height=460)
        
else:
    st.title("Please sign-in to access this feature!")