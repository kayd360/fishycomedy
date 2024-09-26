import streamlit as st
try:
    import yaml
except ImportError:
    yaml = None
from datetime import datetime
import time
from google_sheets import append_to_sheet, get_applicants, get_sheet, update_sheet_status
from email_sender import send_confirmation_email
from utils import generate_confirmation_code, calculate_show_dates
from privacy_policy import show_privacy_policy
from validation import is_valid_email, is_valid_phone, format_phone, background_tasks
from threading import Thread
from credentials import get_credentials

st.set_page_config(page_title="Fishy Comedy Tuesday Night", page_icon="🎭", layout="wide")

credentials = get_credentials()
if credentials is None:
    st.error("Failed to load credentials. The app cannot function properly.")
    st.stop()

st.write("Credentials loaded successfully.")
# st.write("GCP service account keys:", list(credentials['gcp_service_account'].keys()))

ORGANIZER_EMAIL = credentials['organizer_email']
ORGANIZER_PASSWORD = credentials['organizer_password']

def format_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d %b %Y (%a)")
    
def main():
    st.set_page_config(page_title="Fishy Comedy Tuesday Night", page_icon="🎭", layout="wide")
    
    credentials = get_credentials()
    if credentials is None:
        st.error("Failed to load credentials. The app cannot function properly.")
        return

    global ORGANIZER_EMAIL, ORGANIZER_PASSWORD
    ORGANIZER_EMAIL = credentials['organizer_email']
    ORGANIZER_PASSWORD = credentials['organizer_password']
    
    # Custom CSS for button styling
    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        height: 50px;
        border: 1px solid #ddd;
        color: #333;
    }
    .stButton > button:hover {
        background-color: #e0e0e0;
    }
    .stButton > button[kind="primary"] {
        background-color: #90EE90;
        color: #000000;
    }
    .stButton > button[kind="secondary"] {
        background-color: #f0f0f0;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

    # Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Apply for Show", "Organizer Interface", "Privacy Policy"])

    if page == "Apply for Show":
        show_application_form()
    elif page == "Organizer Interface":
        show_organizer_interface()
    elif page == "Privacy Policy":
        show_privacy_policy()

def show_application_form():
    st.title("Fishy Comedy Tuesday Night - Prague")
    st.header("Apply for a Show")
    
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    
    if 'confirmation_code' not in st.session_state:
        st.session_state.confirmation_code = None

    if not st.session_state.form_submitted:
        # Callback functions
        def set_preference(value):
            st.session_state.preference = value

        def set_travelling(value):
            st.session_state.travelling = value

        def toggle_date_selection(date, slot_type):
            key = f"{date}_{slot_type}"
            st.session_state.selected_dates[key] = not st.session_state.selected_dates.get(key, False)

        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email Address")
            stage_name = st.text_input("Stage Name")
        with col2:
            whatsapp = st.text_input("WhatsApp Number (with country code)")
            video_url = st.text_input("Sample Video URL")
        
        # Preference selection
        st.subheader("Preference")
        if 'preference' not in st.session_state:
            st.session_state.preference = None
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("First Half", key="first_half", use_container_width=True, 
                      type="primary" if st.session_state.preference == "First Half" else "secondary",
                      on_click=set_preference, args=("First Half",))
        with col2:
            st.button("Second Half", key="second_half", use_container_width=True,
                      type="primary" if st.session_state.preference == "Second Half" else "secondary",
                      on_click=set_preference, args=("Second Half",))
        with col3:
            st.button("No Preference", key="no_preference", use_container_width=True,
                      type="primary" if st.session_state.preference == "No Preference" else "secondary",
                      on_click=set_preference, args=("No Preference",))

        # Travelling comedian selection
        st.subheader("Are you a travelling comedian?")
        if 'travelling' not in st.session_state:
            st.session_state.travelling = None
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("Yes", key="travelling_yes", use_container_width=True,
                      type="primary" if st.session_state.travelling == "Yes" else "secondary",
                      on_click=set_travelling, args=("Yes",))
        with col2:
            st.button("No", key="travelling_no", use_container_width=True,
                      type="primary" if st.session_state.travelling == "No" else "secondary",
                      on_click=set_travelling, args=("No",))

        agree = st.checkbox("I agree to the Privacy Policy")
        
        # Date and slot selection
        show_dates = calculate_show_dates()
        if 'selected_dates' not in st.session_state:
            st.session_state.selected_dates = {}        
        st.subheader("Select Available Dates and Slot Types")

        # CSS for mobile responsiveness
        st.markdown("""
        <style>
        .date-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            margin-bottom: 10px;
        }
        .date-col {
            flex: 1 1 100%;
            margin-bottom: 5px;
        }
        .button-col {
            flex: 1 1 50%;
            padding: 0 5px;
        }
        @media (min-width: 768px) {
            .date-col {
                flex: 1 1 30%;
            }
            .button-col {
                flex: 1 1 35%;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        for date in show_dates:
            formatted_date = format_date(date)
            location_link = "https://goo.gl/maps/your-location-link-here"  # Replace with actual link
            
            col0, col1, col2 = st.columns(3)
            with col0:
                st.write(f"{formatted_date} | 📍: [Duende Cafe Bar]({location_link})")
                st.write("(^_^)")
            with col1:
                st.button("Open Slot", key=f"open_{date}", use_container_width=True,
                          type="primary" if st.session_state.selected_dates.get(f"{date}_open", False) else "secondary",
                          on_click=toggle_date_selection, args=(date, "open"))
            with col2:
                st.button("Possibly to Host", key=f"host_{date}", use_container_width=True,
                          type="primary" if st.session_state.selected_dates.get(f"{date}_host", False) else "secondary",
                          on_click=toggle_date_selection, args=(date, "host"))
        
        if st.button("Submit Application"):
            # Validate form inputs
            errors = []
            if not email or not is_valid_email(email):
                errors.append("Please enter a valid email address.")
            if not stage_name:
                errors.append("Stage name is mandatory.")
            if not whatsapp:
                errors.append("WhatsApp number is mandatory.")
            else:
                whatsapp = format_phone(whatsapp)
                if not is_valid_phone(whatsapp):
                    errors.append("Please enter a valid WhatsApp number with country code.")
            if not st.session_state.preference:
                errors.append("Please select a preference.")
            if not st.session_state.travelling:
                errors.append("Please indicate if you are a travelling comedian.")
            if not any(st.session_state.selected_dates.values()):
                errors.append("Please select at least one date and slot type.")
            if not agree:
                errors.append("You must agree to the Privacy Policy to submit an application.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Generate confirmation code
                st.session_state.confirmation_code = generate_confirmation_code()

                # Save to Google Sheets with status "Draft"
                append_success = append_to_sheet([email, stage_name, whatsapp, video_url, st.session_state.preference, st.session_state.travelling, str(st.session_state.selected_dates), st.session_state.confirmation_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Draft"])

                if append_success:
                    # Display success message
                    st.success("Application submitted successfully! Please check your email for the confirmation code.")

                    # Start background tasks (including sending confirmation email)
                    Thread(target=background_tasks, args=(email, st.session_state.confirmation_code)).start()

                    # Set form as submitted
                    st.session_state.form_submitted = True
                    st.rerun()
                else:
                    st.error("There was an error submitting your application. Please try again or contact the organizer.")

    else:
        # Show confirmation code input
        st.info("Please enter the confirmation code sent to your email.")
        user_code = st.text_input("Enter confirmation code:")
        confirm_button = st.button("Confirm")

        # Countdown timer
        total_time = 60
        placeholder = st.empty()
        
        for remaining in range(total_time, 0, -1):
            mins, secs = divmod(remaining, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            
            with placeholder.container():
                st.header(f"Time remaining: {time_str}")
                st.progress((total_time - remaining) / total_time)
            
            if confirm_button:
                if user_code == st.session_state.confirmation_code:
                    # Update Google Sheet status to "Confirmed"
                    update_success = update_sheet_status(st.session_state.confirmation_code, "Confirmed")
                    if update_success:
                        st.success("Application confirmed successfully! Google Sheet has been updated.")
                    else:
                        st.warning("Application confirmed, but there was an issue updating the Google Sheet. Please contact the organizer.")
                    placeholder.empty()
                    st.session_state.form_submitted = False
                    return
                else:
                    st.error("Incorrect code. Please try again.")
                    time.sleep(2)
            
            time.sleep(1)
        
        placeholder.empty()
        st.warning("Time expired. Please contact organiser of show (karan360note@gmail.com)")
        if st.button("Try Again"):
            st.session_state.form_submitted = False
            st.rerun()

def update_sheet_status(confirmation_code, status):
    try:
        sheet = get_sheet()
        cells = sheet.findall(confirmation_code)
        for cell in cells:
            sheet.update_cell(cell.row, sheet.col_count, status)  # Assuming status is the last column
        return True
    except Exception as e:
        st.error(f"Error updating Google Sheet: {str(e)}")
        return False
                
def show_organizer_interface():
    st.title("Organizer Interface")
    
    if st.session_state.get('authenticated', False):
        show_applicants()
    else:
        authenticate_organizer()

def authenticate_organizer():
    credentials = get_credentials()
    if credentials is None:
        st.error("Failed to load credentials. Authentication is not possible.")
        return

    password = st.text_input("Enter organizer password", type="password")
    if st.button("Login"):
        if password == credentials['organizer_password']:
            st.session_state.authenticated = True
            show_applicants()
        else:
            st.error("Incorrect password")

def authenticate_organizer():
    password = st.text_input("Enter organizer password", type="password")
    if st.button("Login"):
        if password == config['organizer_password']:
            st.session_state.authenticated = True
            show_applicants()
        else:
            st.error("Incorrect password")

def show_applicants():
    applicants = get_applicants()
    show_dates = calculate_show_dates()
    
    for date in show_dates:
        with st.expander(f"Show Date: {date}"):
            date_string = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            date_applicants = [a for a in applicants if f"{date_string}_open" in a['DATE_TYPE'] or f"{date_string}_host" in a['DATE_TYPE']]
            
            st.write(f"Total Applicants: {len(date_applicants)}")
            
            num_rows = (len(date_applicants) + 3) // 4  # Calculate number of rows needed
            
            for row in range(num_rows):
                cols = st.columns(4)
                
                for i in range(4):
                    idx = row * 4 + i
                    if idx < len(date_applicants):
                        applicant = date_applicants[idx]
                        availability_type = "open" if f"{date_string}_open" in applicant['DATE_TYPE'] else "host"
                        applicant_id = applicant['EMAIL']
                        key = f"applicant_{date}_{applicant_id}"
                        
                        with cols[i]:
                            if key not in st.session_state:
                                st.session_state[key] = False

                            if st.button(
                                f"{applicant['STAGE_NAME']} ({availability_type})",
                                key=f"btn_{key}",
                                use_container_width=True,
                                type="primary" if st.session_state[key] else "secondary",
                            ):
                                st.session_state[key] = not st.session_state[key]
                            
                            # Display applicant details
                            st.markdown(f"**Half:** {applicant['HALF']}")
                            st.markdown(f"[Video]({applicant['VIDEO']})")
                            st.markdown(f"[WhatsApp](https://wa.me/{applicant['PHONE']})")
            
            if st.button(f"Save Draft for {date}", key=f"save_draft_{date}"):
                save_draft(date, date_applicants)
            
            if st.button(f"Send Confirmations for {date}", key=f"send_confirmations_{date}"):
                send_confirmations(date, date_applicants)

def initialize_session_state(applicants, show_dates):
    for date in show_dates:
        date_string = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        for applicant in applicants:
            for availability_type in ['open', 'host']:
                key = f"{date}_{applicant['EMAIL']}_{availability_type}"
                if key not in st.session_state:
                    st.session_state[key] = False

def toggle_applicant_selection(key):
    st.session_state[key] = not st.session_state[key]

def set_applicant_selection(applicant_id, date):
    key = f"applicant_{date}_{applicant_id}"
    st.session_state[key] = not st.session_state.get(key, False)

def save_draft(date, applicants):
    selected_applicants = [a for a in applicants if st.session_state.get(f"applicant_{date}_{a['EMAIL']}", False)]
    st.write(f"Saving draft for {date} with {len(selected_applicants)} selected applicants")
    
    # Update Google Sheet
    sheet = get_sheet()
    for applicant in applicants:
        email = applicant['EMAIL']
        is_selected = f"applicant_{date}_{email}" in st.session_state and st.session_state[f"applicant_{date}_{email}"]
        status = "Selected for Draft" if is_selected else "Not Selected"
        
        # Find the row for this applicant and date
        cell = sheet.find(email)
        date_cell = sheet.find(date)
        if cell and date_cell and cell.row == date_cell.row:
            # Update the status column (assuming it's the last column)
            sheet.update_cell(cell.row, sheet.col_count, status)
    
    st.success(f"Draft saved for {date}. {len(selected_applicants)} applicants marked as selected in Google Sheet.")


def send_confirmations(date, applicants):
    selected_applicants = [a for a in applicants if st.session_state.get(f"applicant_{date}_{a['EMAIL']}", False)]
    st.write(f"Sending confirmations for {date} to {len(selected_applicants)} selected applicants")
    # Add your logic here to send emails and update the Google Sheet

def display_applicant_button(applicant, date, availability_type):
    button_key = f"{date}_{applicant['EMAIL']}_{availability_type}"
    
    if button_key not in st.session_state:
        st.session_state[button_key] = False
    
    button_type = "primary" if st.session_state[button_key] else "secondary"
    st.button(
        f"{applicant['STAGE_NAME']} ({availability_type})",
        on_click=set_applicant_selection, 
        args=(button_key,), 
        type=button_type
    )

    if st.session_state[button_key]:
        with st.expander(f"Details for {applicant['STAGE_NAME']}"):
            st.markdown(f"Half: {applicant['HALF']}")
            st.markdown(f"[Video]({applicant['VIDEO']})")
            st.markdown(f"[WhatsApp](https://wa.me/{applicant['PHONE']})")

if __name__ == "__main__":
    main()