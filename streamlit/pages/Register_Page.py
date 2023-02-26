import streamlit as st
import requests
import json
from streamlit_extras.switch_page_button import switch_page

BASE_URL = "http://localhost:8000"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['access_token'] = ''
    st.session_state['full_name'] = ''
    st.session_state['username'] = ''
    st.session_state['password'] = ''

if st.session_state['logged_in'] == False:
    st.write("Create a new user account to get started !!!")
    
    full_name = st.text_input("Full Name", placeholder='Full Name')
    username = st.text_input("Username", placeholder='Username')
    password = st.text_input("Password", placeholder='Password', type = 'password')
    confirm_password = st.text_input("Confirm Password", type="password")
    register_submit = st.button('Register')

    if register_submit:
        if len(password) < 6:
            st.warning("Password should be minimum 6 characters long")
        elif full_name == '' or username == '' or password == '' or confirm_password == '':
            st.warning("Please fill all fields.")
        elif password != confirm_password:
            with st.spinner("Wait ..."):
                st.warning("Passwords do not match.")
        else:
            with st.spinner("Wait.."):
                try:
                    st.session_state.full_name = full_name
                    st.session_state.username = username
                    st.session_state.password = password
                    register_user = {
                        'full_name': st.session_state.full_name,
                        'username': st.session_state.username,
                        'password': st.session_state.password
                    }
                    response = requests.post(url=f'{BASE_URL}/user/create', json=register_user) 
                except:
                    st.error("Service is unavailable at the moment !!")
                    st.error("Please try again later")
                    st.stop()
                
                if response and response.status_code == 200:
                    st.success("Account created successfully !!")
                    st.session_state.access_token = response.json().get('access_token')
                    st.session_state.logged_in = True
                    switch_page('Login_Page')
                else:
                    st.error("Error: User registration failed!")

    with st.sidebar:
        if st.session_state and st.session_state.logged_in and st.session_state.username:
            st.write(f'Current User: {st.session_state.username}')
        else:
            st.write('Current User: Not Logged In')