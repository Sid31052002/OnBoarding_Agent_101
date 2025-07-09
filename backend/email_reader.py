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
from pdf2image import convert_from_path
import base64
from openai import OpenAI
from id.progress_utils import DOCUMENT_SEQUENCE, load_progress, save_progress

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def ocr_attachment(file_path):
    try:
        if file_path.lower().endswith('.pdf'):
            # Convert PDF pages to images
            images = convert_from_path(file_path)
            text = ""
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image, lang="eng+hin")
                text += f"\n--- Page {i+1} ---\n{page_text}"
            txt_path = file_path + ".txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            return text, txt_path
        else:
            image = Image.open(file_path)
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

def extract_document_fields_with_openai(file_path, doc_type):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        file_b64 = base64.b64encode(file_bytes).decode("utf-8")
    prompt = (
        f"This is a {doc_type.replace('_', ' ')} document for Dubai onboarding. "
        "Extract all relevant fields (e.g., Name, License Number, Expiry Date, etc.) in JSON format. "
        "If a field is missing, write 'Not detected'."
    )
    # For images and PDFs, use image_url; for PDFs, you may want to convert to images and send the first page
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == ".pdf":
        # Convert first page of PDF to image for Vision API
        images = convert_from_path(file_path, first_page=1, last_page=1)
        img = images[0]
        from io import BytesIO
        img_buffer = BytesIO()
        img.save(img_buffer, format="JPEG")
        img_b64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        image_url = f"data:image/jpeg;base64,{img_b64}"
    else:
        image_url = f"data:image/jpeg;base64,{file_b64}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that extracts structured data from Dubai business documents."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

def process_emails():
    for mail in fetch_unread_emails():
        sender = mail["from"]
        body = mail["body"].strip().upper()
        progress = load_progress(sender)

        # Step 1: Wait for "YES" to start onboarding
        if progress["current_step"] == "ask_account_open":
            if "YES" in body:
                progress["current_step"] = DOCUMENT_SEQUENCE[0]
                save_progress(sender, progress)
                send_email(sender, "Please provide your Commercial License", "Reply with your Commercial License as an attachment.")
            else:
                send_email(sender, "Start Onboarding", "Reply 'YES' to begin your onboarding process.")
            continue

        # Step 2: Document collection and confirmation
        current_step = progress["current_step"]
        if current_step in DOCUMENT_SEQUENCE:
            # Check for attachments
            if mail["attachments"]:
                # Save, OCR, extract fields, save JSON, send for confirmation
                for filepath in mail["attachments"]:
                    extracted_data = extract_document_fields_with_openai(filepath, doc_type=current_step)
                    json_path = filepath + ".json"
                    with open(json_path, "w", encoding="utf-8") as f:
                        f.write(extracted_data)
                    send_email(sender, f"Confirm your {current_step.replace('_', ' ').title()} Data", f"Extracted data:\n{extracted_data}\n\nReply 'CONFIRM' if correct or 'REUPLOAD' to upload again.")
                    progress["documents"][current_step] = {"status": "pending_confirmation", "file": filepath, "data": extracted_data}
                    save_progress(sender, progress)
            elif "CONFIRM" in body:
                idx = DOCUMENT_SEQUENCE.index(current_step)
                progress["documents"][current_step]["status"] = "validated"
                if idx + 1 < len(DOCUMENT_SEQUENCE):
                    next_step = DOCUMENT_SEQUENCE[idx + 1]
                    progress["current_step"] = next_step
                    send_email(sender, f"Please provide your {next_step.replace('_', ' ').title()}", f"Reply with your {next_step.replace('_', ' ').title()} as an attachment.")
                else:
                    progress["current_step"] = "completed"
                    send_email(sender, "Onboarding Complete", "Thank you! Your onboarding is complete.")
                save_progress(sender, progress)
            elif "REUPLOAD" in body:
                progress["documents"][current_step] = {"status": "awaiting_upload"}
                send_email(sender, f"Re-upload your {current_step.replace('_', ' ').title()}", f"Please re-upload your {current_step.replace('_', ' ').title()} as an attachment.")
                save_progress(sender, progress)
            else:
                send_email(sender, f"Awaiting {current_step.replace('_', ' ').title()}", f"Please reply with your {current_step.replace('_', ' ').title()} as an attachment.")
            continue

        # Step 3: Completed
        if progress["current_step"] == "completed":
            send_email(sender, "Onboarding Already Complete", "Your onboarding process is already complete.")
