# utils.py
import random
import string
from datetime import datetime, timedelta

def generate_confirmation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def calculate_show_dates(start_date=datetime(2024, 10, 1), num_dates=8):
    dates = []
    current_date = start_date
    while len(dates) < num_dates:
        if current_date.weekday() == 1:  # Tuesday
            dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=14)  # Next show after two weeks
        else:
            current_date += timedelta(days=1)
    return dates