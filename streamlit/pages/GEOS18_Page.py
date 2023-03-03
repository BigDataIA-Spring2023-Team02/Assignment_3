import json
import requests
import streamlit as st
from PIL import Image

if 'username' not in st.session_state:
    st.session_state.username = ''

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    user = "Not Logged In" if st.session_state.username == "" else st.session_state.username
    st.write(f'Current User: {user}')
    logout_button = st.button('Log Out')
    if logout_button:
        st.session_state['logged_in'] = False
        st.experimental_rerun()

if st.session_state['logged_in'] == True:
    st.markdown("<h2 style='text-align: center;'>Data Exploration of the GEOS dataset 🌎</h1>", unsafe_allow_html=True)
    st.header("")
    st.image(Image.open('streamlit/pages/Satellite-data-for-imagery.jpeg'))
    
    BASE_URL = "http://localhost:8000"
    option = st.selectbox('Select the option to search file', ('Select Search Type', 'Search By Field 🔎', 'Search By Filename 🔎'))
    
    if option == 'Select Search Type':
        st.error('Select an input field')
    
    elif option == 'Search By Field 🔎':
        with st.spinner('Wait for it...'):
            st.markdown("<h3 style='text-align: center;'>Search Through Fields 🔎</h1>", unsafe_allow_html=True)
            response = requests.get(f"{BASE_URL}/noaa-database/goes18")
            if response.status_code == 200:
                api_limit_flag = False
                user_plan_response = requests.get(f"{BASE_URL}/user/details?username={st.session_state['username']}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                if user_plan_response.status_code == 200:
                    user_plan = json.loads(user_plan_response.text)
                    try:
                        api_calls = requests.get(f"{BASE_URL}/logs/latest?username={st.session_state['username']}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                    except:
                        st.error("Service unavailable, please try again later")
                        st.stop()
                    if api_calls.status_code == 200:
                        log_response = json.loads(api_calls.text)
                        call_last_hour = len(log_response['timestamp'])
                        
                        if user_plan == ["Free"]:
                            if (int(call_last_hour) >= 10):
                                st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                                st.write("Do you wish to upgrade?")
                                if st.button("Yes"):
                                    check_limit = requests.post(f"{BASE_URL}/user/updateplan?username={st.session_state['username']}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                                    if check_limit.status_code == 200:
                                        st.success("Plan upgraded, please continue.")
                                        with st.spinner("Loading..."): 
                                            st.experimental_rerun()
                                if st.button("No"):
                                    st.session_state['logged_in'] = False
                                    st.experimental_rerun()

                            else:
                                api_limit_flag = True

                        elif user_plan == ["Gold"]:
                            if (int(call_last_hour) >= 15):
                                st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                                st.write("Do you wish to upgrade?")
                                if st.button("Yes"):
                                    check_limit2 = requests.post(f"{BASE_URL}/user/updateplan?username={st.session_state['username']}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                                    if check_limit2.status_code == 200:
                                        st.success("Plan upgraded, please continue.")
                                        with st.spinner("Loading..."): 
                                            st.experimental_rerun()
                                if st.button("No"):
                                    st.session_state['logged_in'] = False
                                    st.experimental_rerun()
                            else:
                                api_limit_flag = True
                
                        elif user_plan == ['Platinum']:
                            api_limit_flag = True

                        else:
                            api_limit_flag = True
            elif response.status_code == 401:
                st.error("Session token expired, please login again")
                st.stop()
            else:
                st.error("Database not populated.")
                st.stop()

            if api_limit_flag:
                json_data = json.loads(response.text)
                products = json_data
            
            product_input = st.selectbox("Product name: ", products, disabled = True, key="selected_product")
            with st.spinner('Loading...'):
                response = requests.get(f"{BASE_URL}/noaa-database/goes18/prod?product={product_input}")
            if response.status_code == 200:
                json_data = json.loads(response.text)
                years = json_data
            else:
                st.error("Incorrect input given, please change")
            
            year_input = st.selectbox("Year for which you are looking to get data for: ", [" "] + years, key="selected_year")
            if (year_input == " "):
                st.warning("Please select a year!")
            else:
                with st.spinner('Loading...'):
                    response = requests.get(f"{BASE_URL}/noaa-database/goes18/prod/year?year={year_input}&product={product_input}")
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    days = json_data
                else:
                    st.error("Incorrect input given, please change")

                day_input = st.selectbox("Day within year for which you want data: ", [" "] + days, key="selected_day")
                if (day_input == " "):
                    st.warning("Please select a day!")
                else:
                    with st.spinner('Loading...'):
                        response = requests.get(f"{BASE_URL}/noaa-database/goes18/prod/year/day?day={day_input}&year={year_input}&product={product_input}")
                    if response.status_code == 200:
                        json_data = json.loads(response.text)
                        hours = json_data
                    else:
                        st.error("Incorrect input given, please change")
                    
                    hour_input = st.selectbox("Hour of the day for which you want data: ", [" "] + hours, key='selected_hour')
                    if (hour_input == " "):
                        st.warning("Please select an hour!")
                    else:
                        with st.spinner("Loading..."):
                            response = requests.get(f"{BASE_URL}/aws-s3-files/goes18?year={year_input}&day={day_input}&hour={hour_input}&product={product_input}")
                        if response.status_code == 200:
                            json_data = json.loads(response.text)
                            files_available = json_data
                        else:
                            st.error("Incorrect input given, please change")

                        file_input = st.selectbox("Select a file: ", files_available, key='selected_file')
                        if st.button('Fetch file ©️'):
                            with st.spinner("Loading..."):
                                response = requests.post(f"{BASE_URL}/aws-s3-files/goes18/copyfile?file_name={file_input}&product={product_input}&year={year_input}&day={day_input}&hour={hour_input}")
                            if response.status_code == 200:
                                json_data = json.loads(response.text)
                                download_url = json_data
                                st.success("File available for download.")
                                st.write("URL to download file:", download_url)
                            else:
                                st.error("Incorrect input given, please change")
    
    elif option == 'Search By Filename 🔎':
        with st.spinner('Wait for it...'):
            st.markdown("<h3 style='text-align: center;'>Search Through Filename 🔎</h1>", unsafe_allow_html=True)
            file_name = st.text_input('NOAA GEOS-18 Filename',)
            if st.button('Fetch file ©️'):
                with st.spinner("Loading..."):
                    response = requests.post(f"{BASE_URL}/aws-s3-fetchfile/goes18?file_name={file_name}")
                if response.status_code == 404:
                    st.warning("No such file exists at GOES18 location")
                elif response.status_code == 400:
                    st.error("Invalid filename format for GOES18")
                else:
                    api_limit_flag = False
                    user_plan_response = requests.get(f"{BASE_URL}/user/details?username={st.session_state['username']}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                    if user_plan_response.status_code == 200:
                        user_plan = json.loads(user_plan_response.text)
                        try:
                            api_calls = requests.get(f"{BASE_URL}/logs/latest?username={st.session_state['username']}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                        except:
                            st.error("Service unavailable, please try again later")
                            st.stop()
                        if api_calls.status_code == 200:
                            log_response = json.loads(api_calls.text)
                            call_last_hour = len(log_response['timestamp'])
                            
                            if user_plan == ["Free"]:
                                if (int(call_last_hour) >= 10):
                                    st.error("You have exhausted the 10 hourly API calls limit. Consider upgrading to the Gold plan!")
                                    st.write("Do you wish to upgrade?")
                                    if st.button("Yes"):
                                        check_limit = requests.post(f"{BASE_URL}/user/updateplan?username={st.session_state['username']}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                                        if check_limit.status_code == 200:
                                            st.success("Plan upgraded, please continue.")
                                            with st.spinner("Loading..."): 
                                                st.experimental_rerun()
                                    if st.button("No"):
                                        st.session_state['logged_in'] = False
                                        st.experimental_rerun()
                                else:
                                    api_limit_flag = True

                            elif user_plan == ["Gold"]:
                                if (int(call_last_hour) >= 15):
                                    st.error("You have exhausted the 15 hourly API calls limit. Consider upgrading to the Platinum plan!")
                                    st.write("Do you wish to upgrade?")
                                    if st.button("Yes"):
                                        check_limit2 = requests.post(f"{BASE_URL}/user/updateplan?username={st.session_state['username']}", headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                                        if check_limit2.status_code == 200:
                                            st.success("Plan upgraded, please continue.")
                                            with st.spinner("Loading..."): 
                                                st.experimental_rerun()
                                    if st.button("No"):
                                        st.session_state['logged_in'] = False
                                        st.experimental_rerun()
                                else:
                                    api_limit_flag = True
                    
                            elif (user_plan == ['Platinum']):
                                api_limit_flag = True
                    
                            else:
                                api_limit_flag = True
                
                if api_limit_flag:
                    json_data = json.loads(response.text)
                    final_url = json_data
                    st.success("Found URL of the file available on GOES bucket!")
                    st.write("URL to file: ", final_url)

else:
    st.title("Please sign-in to access this feature!")