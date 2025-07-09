import os
from supabase import Client, create_client
from backend.models import Customer
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def register_customer(customer: Customer) -> bool:
    try:
        data = {
            "name": customer.name,
            "email": customer.email,
            "phone": str(customer.phone),  
            "business_name": customer.business_name
        }
        response = supabase.table("onboarding").insert(data).execute()
        return response.status_code == 201
    except Exception as e:
        print("Error registering customer:", e)
        return False

def fetch_latest_email():
    response = supabase.table('onboarding').select("*").order("id", desc=True).limit(1).execute()
    if response.data:
        return response.data[0]["email"]
    return None

