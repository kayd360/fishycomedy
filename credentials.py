import streamlit as st

def get_credentials():
    # Debug: Print all available top-level secrets keys
    st.write("Available top-level secrets:", list(st.secrets.keys()))

    # Directly access the nested gcp_service_account
    gcp_service_account = st.secrets.get('gcp_service_account', {})

    # Debug: Print keys in gcp_service_account
    st.write("Keys in gcp_service_account:", list(gcp_service_account.keys()))

    credentials = {
        'organizer_email': st.secrets.get('organizer_email', ''),
        'organizer_password': st.secrets.get('organizer_password', ''),
        'gcp_service_account': gcp_service_account
    }

    # Verify that required fields are present in gcp_service_account
    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url']
    missing_fields = [field for field in required_fields if field not in gcp_service_account]
    
    if missing_fields:
        st.error(f"Missing required fields in gcp_service_account: {', '.join(missing_fields)}")
        st.error("Please check your Streamlit secrets configuration.")
        # Debug: Print the contents of gcp_service_account (excluding private key)
        safe_gcp_service_account = {k: v if k != 'private_key' else '[REDACTED]' for k, v in gcp_service_account.items()}
        st.write("gcp_service_account contents:", safe_gcp_service_account)
        return None
    
    return credentials

# You can add a test function to run this directly
if __name__ == "__main__":
    credentials = get_credentials()
    if credentials:
        st.write("Credentials loaded successfully")
    else:
        st.write("Failed to load credentials")