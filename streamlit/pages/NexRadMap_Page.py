import json
import folium
import requests
import warnings
import streamlit as st
import streamlit_folium as stf

warnings.simplefilter(action='ignore', category=FutureWarning)

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
    st.markdown("<h2 style='text-align: center;'>NexRad Map Geo-Locations 📍</h1>", unsafe_allow_html=True)
    
    BASE_URL = "http://localhost:8000"
    
    with st.spinner('Refreshing map locations ...'):
        
        response = requests.get(f"{BASE_URL}/noaa-database/mapdata")#, headers=headers)
        if response.status_code == 404:
            st.warning("Unable to fetch mapdata")
            st.stop()
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
            map_dict = json_data

        map = folium.Map(location=[40,-100], tiles="OpenStreetMap", zoom_start=4)
        for i in range(0,len(map_dict)):
            folium.Marker(
            location = [map_dict['latitude'][i], map_dict['longitude'][i]],
            popup = (map_dict['Station_Code'][i],map_dict['County'][i])
            ).add_to(map)

        st.markdown("<h2 style='text-align: center;'>Nexrad Station Pointers</h1>", unsafe_allow_html=True)
        stf.st_folium(map, width=700, height=460)
        
else:
    st.title("Please sign-in to access this feature!")