import streamlit as st
import re
import datetime
from airtable import Airtable

BASE_ID = "appQUrbees7orvriu"
API_KEY = "patsJioGGlyzjX95s.9470d22630e0e2729f0cc9b2a5ef20f741741e5fa35f8b6093c48ec2339552e2"
TABLE_NAME = 'login'

airtable = Airtable(BASE_ID, TABLE_NAME, api_key=API_KEY)

# Define global variables
global email, username, password, cnfPassword

# Define session state
class SessionState:
    def __init__(self):
        self.email = None
        self.username = None
        self.authentication_status = False

# Initialize session state
session_state = SessionState()

def insert_user():
    date = str(datetime.datetime.now())
    data = {
        'username': username,
        'email': email,
        'password': password,
        'loginTime': date
    }
    return airtable.insert(data)

def fetch_user():
    records = airtable.get_all()
    return records

def get_email():
    users = airtable.get_all()
    emails = [user['fields']['email'] for user in users]
    return emails

def get_username():
    users = airtable.get_all()
    usernames = [user['fields']['username'] for user in users]
    return usernames

def validate_email(email):
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
    return re.match(pattern, email)

def validate_username(username):
    pattern = "^[a-zA-z0-9]*$"
    return re.match(pattern, username)

def user_signup():
    global email, username, password, cnfPassword

    with st.form(key='signup', clear_on_submit=True):
        st.subheader(':green[Sign UP]')
        email = st.text_input(':blueEmail', placeholder='Email')
        username = st.text_input(':blue[username]', placeholder='Username')
        password = st.text_input(':blue[password]', placeholder='Password', type='password')
        cnfPassword = st.text_input(':blue[cnfPassword]', placeholder='Confirm Password', type='password')

        if email:
            if validate_email(email):
                if email not in get_email():
                    if validate_username(username):
                        if username not in get_username():
                            if len(username) >= 2:
                                if len(password) >= 8:
                                    if password == cnfPassword:
                                        insert_user()
                                        session_state.email = email
                                        session_state.username = username
                                        session_state.authentication_status = True
                                        st.success("User registration successful")
                                    else:
                                        st.warning("Password does not match")
                                else:
                                    st.warning("Password is weak")
                            else:
                                st.warning("Username is too short")
                        else:
                            st.warning("Username already Exists!!!!")
                    else:
                        st.warning("Invalid username!!")
                else:
                    st.warning("Email already Exists!!!!")
            else:
                st.warning("Email is not valid.\nPLEASE ENTER A VALID EMAIL")

        btn1, btn2, btn3, btn4, btn5 = st.columns(5)
        with btn3:
            st.form_submit_button('signup')

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
                # Check if the password matches (replace this with proper password checking logic)
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

def user_signout():
    global authentication_status
    session_state.email = None
    session_state.username = None
    session_state.authentication_status = False
    st.success("You have been successfully signed out!")

def main():
    global authentication_status

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Home", "Login", "Signup"])

    if page == "Home":
        st.title("SkillCraft Homepage")

    elif page == "Login":
        user_login()

    elif page == "Signup":
        user_signup()

    if session_state.authentication_status:
        st.sidebar.write(f"Welcome, {session_state.username}!")
        if st.sidebar.button("LogOut"):
            user_signout()

    st.sidebar.markdown("---")
    st.sidebar.text("👤  " + session_state.username if session_state.authentication_status else "")



if __name__ == "__main__":
    main()



