from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import Customer
from backend.email_utils import send_welcome_email
from backend.crud import register_customer,fetch_latest_email,supabase
from backend.conversation import log_conversation
from backend.id.progress_utils import save_progress, load_progress

app = FastAPI()

@app.get("/")
def start():
    return {'Message':'This is your onboarding agent!'}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             
    allow_credentials=True,          
    allow_methods=["*"],             
    allow_headers=["*"],             
)

@app.post("/register_customer")
async def register(customer:Customer):
    success = register_customer(customer)
    if success is None:
        raise HTTPException(status_code=400, detail="Registration Failed!")

    email = fetch_latest_email()
    if email:
        welcome_message = send_welcome_email(email)
        if welcome_message:
            log_conversation(email, "agent", welcome_message)
            # Initialize onboarding progress
            save_progress(email, {"current_step": "ask_account_open", "documents": {}})
        else:
            print("Email sending failed, skipping conversation log.")
    
    return {"message": "Customer registered and email sent"}

@app.get("/progress/{email}")
def get_progress(email: str):
    progress = load_progress(email)
    return progress

@app.get("/all_users_progress")
def all_users_progress():
    # Fetch all users from the onboarding table
    response = supabase.table("onboarding").select("*").execute()
    users = response.data if hasattr(response, "data") else []
    # Attach progress for each user
    for user in users:
        user["progress"] = load_progress(user["email"])
    return users
