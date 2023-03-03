import os
import json
import boto3
import requests
import streamlit as st
from dotenv import load_dotenv
from requests.exceptions import HTTPError
from fastapi.security import OAuth2PasswordBearer
from streamlit_extras.switch_page_button import switch_page

BASE_URL = "http://localhost:8000"

st.title("Reset Password Page !!!")

user = st.text_input("User Name")
new_password = st.text_input("Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")
reset_button = st.button('Update Password !!!')

if new_password == '' or confirm_password == '':
    st.warning("Please enter all fields")
elif new_password != confirm_password:
    st.warning("New password and confirm password must match")
else:
    with st.spinner("Wait.."):
        payload = {'username': user, 'new_password': new_password, 'confirm_password': confirm_password}
        headers = {'Authorization': f'Bearer {st.session_state["access_token"]}'}
        try:
            response = requests.post(f"{BASE_URL}/reset", json=payload, headers=headers)
            print("UI: Response", response)
        except:
            st.error("Service is unavailable at the moment !!")
            st.error("Please try again later")
            st.stop()

    if response.status_code == 200:
        st.success("Password reset successfully")
        st.session_state['reset_password'] = False
        st.experimental_rerun()
    elif response.status_code == 401:
        st.error("Incorrect current password entered !!")
    else:
        st.error("Failed to reset password")

if reset_button:
    with st.spinner("Loading..."):
        switch_page('Login_Page')