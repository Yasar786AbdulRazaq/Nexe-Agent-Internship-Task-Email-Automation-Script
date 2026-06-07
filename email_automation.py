

import os
import base64
import time
import json
from datetime import datetime
from email.mime.text import MIMEText
import schedule

# Google Libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Agar Gmail mein sirf email bhejna ho to ye scope kafi hai
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Gmail API se authenticate karne aur service build karne ka function"""
    creds = None
    # token.json user ke login credentials ko save rakhta hai
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def log_email_history(to_email, subject, status, error_msg="None"):
    """Feature: Log Email History"""
    log_file = "email_history_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] TO: {to_email} | SUBJECT: {subject} | STATUS: {status} | ERROR: {error_msg}\n"
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(log_entry)
    print(f"\n[LOG] History updated for: {to_email}")

def send_email():
    """Feature: Send to Gmail API"""
    print("\n--- Starting Email Automation Task ---")
    
    to_email = "maryamnaqeeb36@gmail.com" 
    subject = "Automated Professional Update"
    
    body_text = """Hello,\n\nThis is an automated scheduled email.\n\nBest Regards,\nMaryam Naqeeb\nEmail: maryamnaqeeb36@gmail.com\nLinkedIn: Maryam Naqeeb"""

    try:
        service = get_gmail_service()
        message = MIMEText(body_text)
        message['to'] = to_email
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        send_status = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f"Email successfully sent! Message ID: {send_status['id']}")
        
        log_email_history(to_email, subject, "SUCCESS")

    except Exception as e:
        print(f"Failed to send email. Error: {e}")
        log_email_history(to_email, subject, "FAILED", str(e))

# ==========================================
# Exact 3 minutes aage ka time set kiya hai (Raat ke 9:00 PM)
# ==========================================
schedule.every().day.at("21:08").do(send_email)

print("===== Email Automation Script Running =====")
print("Target Time Set: 21:08 (Raat ke 9:08 PM)")
print("--------------------------------------------")

try:
    while True:
        current_now = datetime.now().strftime("%H:%M:%S")
        print(f"\rCurrent Time: {current_now} | Waiting for 21:08... ", end="", flush=True)
        
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nScript stopped by user.")