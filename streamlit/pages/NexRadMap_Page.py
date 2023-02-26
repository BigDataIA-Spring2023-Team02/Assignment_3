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