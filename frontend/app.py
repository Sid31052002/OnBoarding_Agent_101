import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BaseURL = os.getenv('BaseURL')
SUBMISSION_END_POINT = os.getenv('SUBMISSION_END_POINT')

st.title("Customer Onboarding")

with st.form("registration_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    business_name = st.text_input("Business Name")

    submitted = st.form_submit_button("Register")

    if submitted:
        try:
            phone_int = int(phone)
        except ValueError:
            st.error("Phone number must be numeric.")
            st.stop()
        
        if len(phone) != 10 or not phone.isdigit() or phone_int < 6000000000:
            st.error("Please enter a valid 10-digit Indian mobile number.")
            st.stop()

        payload = {
            "name": name,
            "email": email,
            "phone": phone_int,
            "business_name": business_name
        }

        try:
            response = requests.post(f"{BaseURL}{SUBMISSION_END_POINT}", json=payload)
            if response == 400:
                st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
            else:
                st.success("Customer registered successfully!")
        except Exception as e:
            st.error(f"Request failed: {str(e)}")
