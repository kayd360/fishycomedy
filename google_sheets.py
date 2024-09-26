import gspread
from google.oauth2.service_account import Credentials
from constants import GOOGLE_SHEETS_URL
import ast
import streamlit as st
import logging
from credentials import get_credentials

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_sheet(worksheet_name='new_app_data'):
    logger.info("Entered get_sheet")
    credentials = get_credentials()
    creds = Credentials.from_service_account_info(
        credentials['gcp_service_account'],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    spreadsheet_id = GOOGLE_SHEETS_URL.split('/')[5]
    spreadsheet = client.open_by_key(spreadsheet_id)
    logger.info("completed spreadsheet identification")
    return spreadsheet.worksheet(worksheet_name)

def append_to_sheet(data):
    try:
        sheet = get_sheet()
        
        logger.info("Attempting to append data to Google Sheet")
        st.write("Attempting to append data to Google Sheet")
        
        print("Data being appended:", data)
        st.write(f"Data being appended: {data}")
        
        # Extract the selected dates dictionary
        selected_dates = ast.literal_eval(data[6])
        
        # Create base data without selected dates
        base_data = data[:6] + data[7:-1]  # Exclude the last item (Draft status)
        
        rows_appended = 0
        for date, value in selected_dates.items():
            if value:
                # Create a row with all data including the specific date
                row = base_data + [date, str(value), data[-1]]  # Add Draft status at the end
                sheet.append_row(row)
                rows_appended += 1
                logger.info(f"Appended row for date {date}")
                st.write(f"Appended row for date {date}")
        
        if rows_appended > 0:
            logger.info(f"Successfully appended {rows_appended} rows to Google Sheet")
            st.success(f"Successfully appended {rows_appended} rows to Google Sheet")
            return True
        else:
            logger.warning("No rows were appended to the Google Sheet")
            st.warning("No rows were appended to the Google Sheet")
            return False
        
    except Exception as e:
        error_message = f"Error appending data to Google Sheet: {str(e)}"
        logger.error(error_message)
        st.error(error_message)
        return False

def get_applicants():
    sheet = get_sheet()
    records = sheet.get_all_records()
    
    # Group records by email to combine multiple rows into one applicant
    grouped_records = {}
    for record in records:
        email = record['EMAIL']
        if email not in grouped_records:
            grouped_records[email] = record.copy()
            grouped_records[email]['DATE_TYPE'] = {}
        grouped_records[email]['DATE_TYPE'][record['DATE_TYPE']] = record['VALUE'] == 'TRUE'
    
    result = list(grouped_records.values())
    print(f"Grouped records: {result}")  # Debug print
    return result

def update_sheet_status(confirmation_code, status):
    try:
        sheet = get_sheet()
        cells = sheet.findall(confirmation_code, in_column=8)  # Assuming confirmation code is in column H
        for cell in cells:
            sheet.update_cell(cell.row, 10, status)  # Update status in column J
        return True
    except Exception as e:
        print(f"Error updating Google Sheet: {str(e)}")
        return False