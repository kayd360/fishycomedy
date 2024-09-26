import os
import yaml
import json
import streamlit as st

def get_credentials():
    # Check if running on Streamlit Cloud
    if 'STREAMLIT_SHARING' in os.environ:
        credentials = {
            'organizer_email': st.secrets['organizer_email'],
            'organizer_password': st.secrets['organizer_password'],
            'gcp_service_account': st.secrets['gcp_service_account']
        }
    else:
        # Load local credentials
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            with open('fishyintegration-b047f264e30d.json', 'r') as f:
                gcp_service_account = json.load(f)
            
            credentials = {
                'organizer_email': config['organizer_email'],
                'organizer_password': config['organizer_password'],
                'gcp_service_account': gcp_service_account
            }
        except FileNotFoundError:
            # If local files are not found, use environment variables or default values
            credentials = {
                'organizer_email': os.environ.get('ORGANIZER_EMAIL', 'default@example.com'),
                'organizer_password': os.environ.get('ORGANIZER_PASSWORD', 'default_password'),
                'gcp_service_account': json.loads(os.environ.get('GCP_SERVICE_ACCOUNT', '{}'))
            }
    
    return credentials