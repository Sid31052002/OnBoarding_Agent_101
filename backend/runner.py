# import schedule, time
# from email_reader import fetch_latest_user_email
# from conversation import log_conversation, fetch_conversation
# from generator import generate_agent_response
# from email_utils import send_email

# def process_email():
#     email_data = fetch_latest_user_email()
#     if not email_data:
#         return

#     sender = email_data["from_email"]
#     message = email_data["body"]

#     log_conversation(sender, "human", message)
#     history = fetch_conversation(sender)
#     agent_reply = generate_agent_response(history, message)
#     log_conversation(sender, "agent", agent_reply)
#     send_email(to=sender, subject="RE: Savings Account Assistance", body=agent_reply)

# schedule.every(30).seconds.do(process_email)

# if __name__ == "__main__":
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
