import streamlit as st
from airtable import Airtable
import hr_bot as hr_bot
from st_pages import hide_pages
from session_states import init_assistant
from streamlit_extras.stylable_container import stylable_container
init_assistant()
st.set_page_config(
    layout='wide'
)
st.session_state["botName"]="HR bot"
def hr_chat():
    st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )
    hide_pages(['Intro'])
    hide_pages(['Code'])
    hide_pages(['HR'])
    hide_pages(['Aptitude'])

    with stylable_container(
        key="chat_container",
        css_styles="""
            {
                display: flex !important;
                /*center align*/
                position: fixed !important;
                left: 25% !important;
            

            }
            """,
    ):
        hr_bot.mainGPT(st.session_state["hr_thread_id"], 
            st.session_state["client"], st.session_state["model"],st.session_state["botName"])
hr_chat()
            
