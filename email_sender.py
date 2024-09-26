# email_sender.py
import requests
from constants import GOOGLE_APP_SCRIPT_URL

def send_confirmation_email(email, confirmation_code):
    payload = {
        'email': email,
        'confirmationCode': confirmation_code
    }
    response = requests.post(GOOGLE_APP_SCRIPT_URL, json=payload)
    return response.status_code == 200