import time
from backend.app.services.email_receiver import fetch_unseen_emails

if __name__ == "__main__":
    while True:
        print("Checking for new emails...")
        fetch_unseen_emails()
        time.sleep(30)  # Check every 30 seconds