import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages, hide_pages
import time
import whisper
import pyaudio
from airtable import Airtable
import openai
import os
import threading


st.set_page_config(initial_sidebar_state="auto", layout='wide',page_title="SkillCraft",page_icon="🎮")
#hide sidebar
st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

def init_assistant():
    if "init" not in st.session_state:
        client = openai.OpenAI(api_key=st.secrets['OPENAI_API'])
        st.session_state["client"] = client
        thread = client.beta.threads.create(
            messages=[
            {
            "role": "user",
            "content": "Chat Begins",
            }
        ]
        )
        st.session_state["thread_id"] = thread.id
        st.session_state["assistant_id"] = "asst_yyHIOR8BX2rbgHkRDLmq3W54"
        st.session_state["BASE_ID"] = st.secrets['BASE_ID']
        st.session_state["API_KEY"] = st.secrets['API_KEY']
        airtable_categories = Airtable(st.session_state["BASE_ID"], "categories", api_key=st.session_state["API_KEY"])
        airtable_questions = Airtable(st.session_state["BASE_ID"], "questions", api_key=st.session_state["API_KEY"])
        st.session_state["airtable_categories"] = airtable_categories
        st.session_state["airtable_questions"] = airtable_questions
        categories = st.session_state["airtable_categories"].get_all()
        st.session_state["categories"] = [category['fields']['cname'] for category in categories]
        st.session_state["model"] = whisper.load_model("small", device='cuda:0')
        st.session_state["audio"] = pyaudio.PyAudio()
        st.session_state["init"] = True
        return st.session_state
init_assistant()

st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )
show_pages([
    Page("app.py","Intro"),
    Page("practice.py","Code")
])

hide_pages(['Code'])

#read css file
print(st.session_state["css_displayed"] if "css_displayed" in st.session_state else "First run")
if "css_displayed" not in st.session_state or st.session_state["css_displayed"] == False:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        st.session_state["css_displayed"] = True
    st.markdown('<span style="color: aqua;">S</span>kill<span style="color: aqua;">C</span>raft', unsafe_allow_html=True)
    st.markdown('<p style="margin-top:10px;font-size:30px;">An LLM powered interview preparation platform</p>',unsafe_allow_html=True)
#scroll down button - doesnt work
b1=st.button('↓', key='scroll_down')


#content buttons
st.header("Content")
with st.container():
    col1, col2, col3 = st.columns(3)
    if col1.button("Code"):
        switch_page("Code")
    col1.progress(0.5, "50%")
    apt= col2.button("Aptitude")
    col2.progress(0.6, "60%")
    code= col3.button("HR")
    col3.progress(0.7, "72%")