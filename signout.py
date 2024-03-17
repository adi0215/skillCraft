import streamlit as st

class SessionState:
    def __init__(self):
        self.email = None
        self.username = None
        self.authentication_status = False

session_state = SessionState()

def user_signout():
    session_state.email = None
    session_state.username = None
    session_state.authentication_status = False
    st.success("You have been successfully signed out!")
