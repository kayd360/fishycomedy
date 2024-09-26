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
        # Debug: Print all available secrets
        st.write("Available secrets:", list(st.secrets.keys()))
        
        # Directly access the nested gcp_service_account
        gcp_service_account = st.secrets.get('gcp_service_account', {})
        
        # Debug: Print keys in gcp_service_account
        st.write("Keys in gcp_service_account:", list(gcp_service_account.keys()))
        
        credentials = {
            'organizer_email': st.secrets.get('organizer_email', ''),
            'organizer_password': st.secrets.get('organizer_password', ''),
            'gcp_service_account': gcp_service_account
        }
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
                'organizer_email': config.get('organizer_email', ''),
                'organizer_password': config.get('organizer_password', ''),
                'gcp_service_account': gcp_service_account
            }
        except FileNotFoundError:
            # If local files are not found, use environment variables or default values
            credentials = {
                'organizer_email': os.environ.get('ORGANIZER_EMAIL', ''),
                'organizer_password': os.environ.get('ORGANIZER_PASSWORD', ''),
                'gcp_service_account': json.loads(os.environ.get('GCP_SERVICE_ACCOUNT', '{}'))
            }
    
    # Verify that required fields are present in gcp_service_account
    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url']
    missing_fields = [field for field in required_fields if field not in credentials['gcp_service_account']]
    
    if missing_fields:
        st.error(f"Missing required fields in gcp_service_account: {', '.join(missing_fields)}")
        st.error("Please check your Streamlit secrets or local configuration.")
        # Debug: Print the contents of gcp_service_account (excluding private key)
        safe_gcp_service_account = {k: v if k != 'private_key' else '[REDACTED]' for k, v in credentials['gcp_service_account'].items()}
        st.write("gcp_service_account contents:", safe_gcp_service_account)
        return None
    
    return credentials