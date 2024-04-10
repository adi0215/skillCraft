import streamlit as st
import pyaudio
import whisper
import openai
from airtable import Airtable

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
        apt_thread = client.beta.threads.create(
            messages=[
            {
            "role": "user",
            "content": "Chat Begins",
            }
        ]
        )
        st.session_state["thread_id"] = thread.id
        st.session_state["apt_thread_id"] = apt_thread.id
        st.session_state["apt_assistant_id"] = "asst_FJ9BDUSunTsXUoNwxpu0O4Nz"
        st.session_state["BASE_ID"] = st.secrets['BASE_ID']
        st.session_state["API_KEY"] = st.secrets['API_KEY']
        airtable_categories = Airtable(st.session_state["BASE_ID"], "categories", api_key=st.session_state["API_KEY"])
        airtable_questions = Airtable(st.session_state["BASE_ID"], "questions", api_key=st.session_state["API_KEY"])
        aptitude_questions = Airtable(st.session_state["BASE_ID"], "aptitude", api_key=st.session_state["API_KEY"])
        aptitude_categories = Airtable(st.session_state["BASE_ID"], "aptitude_categories", api_key=st.session_state["API_KEY"])
        hr_questions = Airtable(st.session_state["BASE_ID"], "hr_questions", api_key=st.session_state["API_KEY"])
        st.session_state["aptitude_categories"] = aptitude_categories
        st.session_state["aptitude_questions"] = aptitude_questions
        st.session_state["hr_questions"] = [q['fields']['HR questions'] for q in hr_questions.get_all()]
        st.session_state["airtable_categories"] = airtable_categories
        st.session_state["airtable_questions"] = airtable_questions
        categories = st.session_state["airtable_categories"].get_all()
        apti_categories = st.session_state["aptitude_categories"].get_all()
        st.session_state["apti_categories"] = [category['fields']['categories'] for category in apti_categories]
        st.session_state["categories"] = [category['fields']['cname'] for category in categories]
        st.session_state["loaded_apti_categories"] = {}
        st.session_state["model"] = whisper.load_model("small")
        st.session_state["audio"] = pyaudio.PyAudio()
        st.session_state["init"] = True
        if 'nextqButton' not in st.session_state:
            st.session_state.nextqButton = False
        if 'end_quiz' not in st.session_state:
            st.session_state.end_quiz = False 
        return st.session_state

def apti_init():
    st.session_state.current_question = 0
    st.session_state.player_score = 0