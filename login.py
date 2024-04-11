import streamlit as st
import re
from airtable import Airtable

BASE_ID = "appQUrbees7orvriu"
API_KEY = "patsJioGGlyzjX95s.9470d22630e0e2729f0cc9b2a5ef20f741741e5fa35f8b6093c48ec2339552e2"
LOGIN_TABLE = 'login'

airtable = Airtable(BASE_ID, LOGIN_TABLE, api_key=API_KEY)

class SessionState:
    def __init__(self):
        self.email = None
        self.username = None
        self.authentication_status = False

session_state = SessionState()

def user_login():
    global email, password

    with st.form(key='login', clear_on_submit=True):
        st.subheader(':green[Login]')
        email = st.text_input(':blueEmail', placeholder='Email')
        password = st.text_input(':blue[password]', placeholder='Password', type='password')
        st.form_submit_button("Login")

    if email:
        if validate_email(email):
            if email in get_email():
                user_record = airtable.search('email', email)[0]
                if user_record['fields']['password'] == password:
                    session_state.email = email
                    session_state.username = user_record['fields']['username']
                    session_state.authentication_status = True
                    st.success("Login successful!")
                else:
                    session_state.authentication_status = False
                    st.warning("Incorrect email or password")
            else:
                st.warning("Email does not exist. Please Signup")
        else:
            st.warning("Invalid email")

def get_email():
    users = airtable.get_all()
    emails = [user['fields']['email'] for user in users if 'fields' in user and 'email' in user['fields']]
    return emails

def validate_email(email):
    pattern = r"^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
    return re.match(pattern, email)
