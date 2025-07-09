from supabase import Client, create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def log_conversation(email:str, role:str, message:str) -> bool:
    try:
        data = {"email":email, "role":role, "message":message}
        response = supabase.table("conversation_log").insert(data).execute()
        return True
    except Exception as e:
        print("Failed to log conversation: ",e)
        return False
    
def fetch_conversation(email:str):
    response = supabase.table('conversation_log').select("*").eq("email", email).order("created_at").execute()
    return response.data
