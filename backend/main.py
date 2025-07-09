from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import Customer
from backend.email_utils import send_welcome_email
from backend.crud import register_customer,fetch_latest_email
from backend.conversation import log_conversation

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
        else:
            print("Email sending failed, skipping conversation log.")
    
    return {"message": "Customer registered and email sent"}
