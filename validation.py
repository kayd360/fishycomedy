import re
from threading import Thread
from email_sender import send_confirmation_email

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    pattern = r'^\+\d{1,3}\d{6,14}$'
    return re.match(pattern, phone) is not None

def format_phone(phone):
    if phone.startswith('+'):
        return phone
    return f"+420{phone}"

def background_tasks(email, confirmation_code):
    # Send confirmation email
    send_confirmation_email(email, confirmation_code)
    # You can add more background tasks here if needed