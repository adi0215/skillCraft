import streamlit as st
import re
import datetime
from airtable import Airtable
import streamlit_authenticator as atauth

BASE_ID = "appQUrbees7orvriu"
API_KEY = "patsJioGGlyzjX95s.9470d22630e0e2729f0cc9b2a5ef20f741741e5fa35f8b6093c48ec2339552e2"
TABLE_NAME = 'login'

airtable = Airtable(BASE_ID, TABLE_NAME, api_key=API_KEY)

global email, username, password, cnfPassword

# Define a global variable to store authentication status
authentication_status = False


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
    emails = []
    for user in users:
        emails.append(user['fields']['email'])
    return emails


def get_username():
    users = airtable.get_all()
    usernames = []
    for user in users:
        usernames.append(user['fields']['username'])
    return usernames


def validate_email(email):
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
    if re.match(pattern, email):
        return True
    else:
        return False


def validate_username(username):
    pattern = "^[a-zA-z0-9]*$"
    if re.match(pattern, username):
        return True
    else:
        return False


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
                                        st.success("User registration sucessful")
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
    global email, password, authentication_status

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
                    authentication_status = True
                    st.success("Login successful!")
                else:
                    authentication_status = False
                    st.warning("Incorrect email or password")
            else:
                st.warning("Email does not exist. Please Signup")
        else:
            st.warning("Invalid email")




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


if __name__ == "__main__":
    main()
