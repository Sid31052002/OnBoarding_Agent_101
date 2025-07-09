import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
from conversation import log_conversation, fetch_conversation
from generator import generate_agent_response
from email_utils import send_email
import pytesseract
from PIL import Image
import base64
from openai import OpenAI

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def ocr_attachment(file_path):
    try:
        image = Image.open(file_path)
        # Use both English and Hindi for OCR
        text = pytesseract.image_to_string(image, lang="eng+hin")
        txt_path = file_path + ".txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        return text, txt_path
    except Exception as e:
        print(f"OCR failed for {file_path}: {e}")
        return "", None

def extract_aadhaar_details_with_openai(image_path):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    prompt = (
        "This is an image of an Indian Aadhaar card. "
        "Extract the following fields and format them as:\n"
        "Name: <name>\nDOB: <date of birth>\nGender: <gender>\nAadhaar Number: <number>\n"
        "If any field is missing, write 'Not detected'."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that extracts structured data from aadhar card. Ensure the name, birth date, address, aadhar number to be extracted in a structred format`."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

def fetch_unread_emails():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    imap.select("inbox")

    status, messages = imap.search(None, '(UNSEEN)')
    mail_ids = messages[0].split()

    emails = []
    for num in mail_ids:
        status, msg_data = imap.fetch(num, "(RFC822)")
        raw_msg = msg_data[0][1]
        msg = email.message_from_bytes(raw_msg)

        sender = email.utils.parseaddr(msg["From"])[1]
        subject, _ = decode_header(msg["Subject"])[0]
        subject = subject.decode() if isinstance(subject, bytes) else subject

        body = ""
        attachments = []
        ocr_texts = []
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = part.get("Content-Disposition")
                if part.get_content_type() == "text/plain" and content_disposition is None:
                    body = part.get_payload(decode=True).decode()
                elif content_disposition and "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        # Create directory for sender if not exists
                        save_dir = os.path.join("backend", "id", sender)
                        os.makedirs(save_dir, exist_ok=True)
                        filepath = os.path.join(save_dir, filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        attachments.append(filepath)
                        # OCR processing
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.pdf')):
                            ocr_text, txt_path = ocr_attachment(filepath)
                            if ocr_text:
                                ocr_texts.append((ocr_text, txt_path))
                        # Aadhaar extraction using OpenAI Vision
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                            extracted_text = extract_aadhaar_details_with_openai(filepath)
                            if extracted_text:
                                ocr_texts.append((extracted_text, None))
        else:
            body = msg.get_payload(decode=True).decode()

        emails.append({
            "from": sender,
            "subject": subject,
            "body": body,
            "attachments": attachments,
            "ocr_texts": ocr_texts
        })

    imap.logout()
    return emails

def format_ocr_text(ocr_text):
    # Remove excessive whitespace and blank lines
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
    formatted = "\n".join(f"- {line}" for line in lines)
    return formatted

def process_emails():
    for mail in fetch_unread_emails():
        sender = mail["from"]
        body = mail["body"]

        log_conversation(sender, "human", body)

        history = fetch_conversation(sender)
        reply = generate_agent_response(history, body)

        # If Aadhaar details exist, send them for confirmation
        if mail.get("ocr_texts"):
            for ocr_text, txt_path in mail["ocr_texts"]:
                confirm_msg = (
                    "We have extracted the following details from your Aadhaar card attachment:\n\n"
                    f"{ocr_text}\n\n"
                    "Please confirm if these details are correct."
                )
                send_email(sender, "Please Confirm Your Aadhaar Details", confirm_msg)
                log_conversation(sender, "agent", confirm_msg)
        else:
            send_email(sender, "Re: Your Query", reply)
            log_conversation(sender, "agent", reply)

if __name__ == "__main__":
    process_emails()
