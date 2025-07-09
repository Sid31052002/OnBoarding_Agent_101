import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BaseURL = os.getenv('BaseURL')
SUBMISSION_END_POINT = os.getenv('SUBMISSION_END_POINT')

# Define the document sequence for the onboarding process
DOCUMENT_SEQUENCE = [
    "commercial_license",
    "eid_resident_card",
    "trade_license"
]

st.set_page_config(page_title="Onboarding Dashboard", page_icon="📝", layout="centered")
st.title("🏦 Customer Onboarding Dashboard")

# Registration form
with st.form("registration_form"):
    st.header("Register New Customer")
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
            if response.status_code == 200:
                st.success("Registration successful! Please check your email for next steps.")
            else:
                st.error("Registration failed. Please try again.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Onboarding Progress Dashboard ---
st.header("📊 Track Your Onboarding Progress")
progress_email = st.text_input("Enter your registered email to check progress:")

if st.button("Check Progress"):
    if not progress_email:
        st.warning("Please enter your email.")
    else:
        try:
            resp = requests.get(f"{BaseURL}/progress/{progress_email}")
            if resp.status_code == 200:
                progress = resp.json()
                current_step = progress.get('current_step', 'N/A')
                docs = progress.get("documents", {})

                # Calculate progress
                if current_step == "ask_account_open":
                    step_idx = 0
                elif current_step == "completed":
                    step_idx = len(DOCUMENT_SEQUENCE)
                else:
                    try:
                        step_idx = DOCUMENT_SEQUENCE.index(current_step) + 1
                    except ValueError:
                        step_idx = 0

                st.markdown("#### Progress")
                st.progress(step_idx / len(DOCUMENT_SEQUENCE))

                # Stepper visualization
                st.markdown("#### Onboarding Steps")
                for idx, step in enumerate(DOCUMENT_SEQUENCE):
                    step_name = step.replace("_", " ").title()
                    status = docs.get(step, {}).get("status", "pending")
                    if current_step == "completed" or docs.get(step, {}).get("status") == "validated":
                        st.success(f"✅ {step_name} - Validated")
                    elif current_step == step:
                        st.info(f"🟡 {step_name} - In Progress")
                    elif status == "pending_confirmation":
                        st.warning(f"⏳ {step_name} - Awaiting Confirmation")
                    elif status == "awaiting_upload":
                        st.warning(f"📤 {step_name} - Awaiting Upload")
                    else:
                        st.write(f"⬜ {step_name} - Pending")

                # Document details
                st.markdown("#### Document Details")
                if docs:
                    for doc, info in docs.items():
                        with st.expander(f"{doc.replace('_', ' ').title()} Details"):
                            st.write(f"**Status:** `{info.get('status', 'pending')}`")
                            if info.get("file"):
                                st.write(f"**File:** `{info['file']}`")
                            if info.get("data"):
                                st.code(info["data"], language="json")
                else:
                    st.info("No documents uploaded yet.")

                if current_step == "completed":
                    st.balloons()
                    st.success("🎉 Onboarding Completed!")
            else:
                st.error("Could not fetch progress. Please check your email and try again.")
        except Exception as e:
            st.error(f"Error: {e}")
