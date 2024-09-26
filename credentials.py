import os
import json
import streamlit as st

try:
    from ruamel.yaml import YAML
    yaml = YAML(typ='safe')
except ImportError:
    yaml = None

def get_credentials():
    # Check if running on Streamlit Cloud
    if 'STREAMLIT_SHARING' in os.environ:
        credentials = {
            'organizer_email': st.secrets['organizer_email'],
            'organizer_password': st.secrets['organizer_password'],
        }
        
        # Parse gcp_service_account from st.secrets
        gcp_service_account = {}
        for key in ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url', 'universe_domain']:
            if key in st.secrets['gcp_service_account']:
                gcp_service_account[key] = st.secrets['gcp_service_account'][key]
        
        credentials['gcp_service_account'] = gcp_service_account

    else:
        # Load local credentials
        try:
            if yaml:
                with open('config.yaml', 'r') as f:
                    config = yaml.load(f)
            else:
                # Fallback to JSON if YAML is not available
                with open('config.json', 'r') as f:
                    config = json.load(f)
            
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
    
    # Verify that required fields are present in gcp_service_account
    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url']
    for field in required_fields:
        if field not in credentials['gcp_service_account']:
            raise ValueError(f"Missing required field in gcp_service_account: {field}")
    
    return credentials