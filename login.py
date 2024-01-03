import streamlit as st
from airtable import Airtable
import re
import datetime



AIRTABLE_API_KEY = 'patsJioGGlyzjX95s.9470d22630e0e2729f0cc9b2a5ef20f741741e5fa35f8b6093c48ec2339552e2'
AIRTABLE_BASE_ID = 'appQUrbees7orvriu'
AIRTABLE_TABLE_NAME = 'login'


airtable = Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, api_key=AIRTABLE_API_KEY)

def signup():
    st.title("Signup")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    email = st.text_input("Email:")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.warning("Invalid email address")

    if st.button("Signup"):
        date=str(datetime.datetime.now())
        if not airtable.search('Username', username):
            airtable.insert({'username': username, 'password': password, 'email': email,'loginTime':date})
            st.success("Signup successful! Please login.")
        else:
            st.error("Username already exists. Please choose a different one.")

def login():
    st.title("Login")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    session_state = st.session_state

    if st.button("Login"):
        user_record = airtable.match('Username', username)
        if user_record:
            if user_record['fields']['password'] == password:
                st.success("Login successful!")
            else:
                st.error("Login failed. Please check your credentials.")
        else:
            st.session_state.login_redirect = True
            st.warning("User not found. Please go to signup page in navigation bar.")
            

    if st.button("Forgot Password?"):
        st.text_input("Enter your email:")
        st.warning("A password reset link has been sent to your email. (In a real-world scenario, send an email with a reset link)")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Home", "Login", "Signup"])

    if page == "Home":
        st.title("Welcome to the Streamlit Multi-Page App!")
        st.write("Explore the Login and Signup pages using the sidebar.")

    elif page == "Login":
        login()
        if hasattr(st.session_state, 'login_redirect') and st.session_state.login_redirect:
            st.session_state.login_redirect = False
            
    elif page == "Signup":
        signup()

if __name__ == "__main__":
    main()



# import streamlit as st
# import datetime
# from airtable import Airtable
# import re

# AIRTABLE_API_KEY = 'patsJioGGlyzjX95s.9470d22630e0e2729f0cc9b2a5ef20f741741e5fa35f8b6093c48ec2339552e2'
# AIRTABLE_BASE_ID = 'appQUrbees7orvriu'
# AIRTABLE_TABLE_NAME = 'login'

# airtable = Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, api_key=AIRTABLE_API_KEY)

# def signup():
#     st.title("Signup")

#     session_state = st.session_state
#     if not hasattr(session_state, 'signup_username'):
#         session_state.signup_username = ""
#     if not hasattr(session_state, 'signup_password'):
#         session_state.signup_password = ""
#     if not hasattr(session_state, 'signup_email'):
#         session_state.signup_email = ""

#     session_state.signup_username = st.text_input("Username:", value=session_state.signup_username)
#     session_state.signup_password = st.text_input("Password:", type="password", value=session_state.signup_password)
#     session_state.signup_email = st.text_input("Email:", value=session_state.signup_email)
    
#     if not re.match(r"[^@]+@[^@]+\.[^@]+", session_state.signup_email):
#         st.warning("Invalid email address")

#     if st.button("Signup"):
#         date=str(datetime.datetime.now())
#         if not airtable.search('Username', session_state.signup_username):
#             airtable.insert({'username': session_state.signup_username,
#                              'password': session_state.signup_password,
#                              'email': session_state.signup_email})
#             st.success("Signup successful! Please login.")
#             session_state.signup_username = ""
#             session_state.signup_password = ""
#             session_state.signup_email = ""
#         else:
#             st.error("Username already exists. Please choose a different one.")

# def login():
#     st.title("Login")

#     session_state = st.session_state
#     if not hasattr(session_state, 'login_username'):
#         session_state.login_username = ""
#     if not hasattr(session_state, 'login_password'):
#         session_state.login_password = ""

#     session_state.login_username = st.text_input("Username:", value=session_state.login_username)
#     session_state.login_password = st.text_input("Password:", type="password", value=session_state.login_password)

#     if st.button("Login"):
#         user_record = airtable.match('Username', session_state.login_username)
#         if user_record:
#             if user_record['fields']['password'] == session_state.login_password:
#                 st.success("Login successful!.You can go to homepage")
#             else:
#                 st.error("Login failed. Please check your credentials.")
#         else:
#             st.warning("User not found.Signup for new user i navigation bar.")
#             session_state.login_redirect = True

#     if st.button("Forgot Password?"):
#         st.text_input("Enter your email:")
#         st.warning("A password reset link has been sent to your email.")

# def main():
#     st.sidebar.title("Navigation")
#     page = st.sidebar.selectbox("Select a page", ["Home", "Login", "Signup"])

#     if page == "Home":
#         st.title("Skillcraft Homepage")

#     elif page == "Login":
#         login()
#         if hasattr(st.session_state, 'login_redirect') and st.session_state.login_redirect:
#             st.session_state.login_redirect = False

#     elif page == "Signup":
#         signup()

# if __name__ == "__main__":
#     main()
