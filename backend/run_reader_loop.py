import time
from email_reader import process_emails 

if __name__ == "__main__":
    while True:
        print("Checking for new emails...")
        process_emails()
        time.sleep(30)  