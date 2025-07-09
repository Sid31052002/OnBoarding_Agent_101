import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(to_mail, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_mail
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_mail}")
        return body
    except Exception as e:
        print(f"Failed to send email to {to_mail}: {str(e)}")
        return False


def send_welcome_email(to_mail):
    subject = "Welcome to Linum Labs!"
    body = (
        "Hi there,\n\n"
        "Thank you for signing up with us. We're excited to have you onboard!\n\n"
        "- Team Linum Labs"
    )
    return send_email(to_mail, subject, body)
