import streamlit as st
from airtable import Airtable
import openai
import st_app as st_app
from sandbox import custom_btns
from code_editor import code_editor
from st_pages import hide_pages
import whisper
import pyaudio

hide_pages(['Code'])
hide_pages(['Intro'])

import os

""" ANY VARIABLES THAT PERSIST THROUGH THE SESSION SHOULD BE DEFINED HERE """
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
init_assistant()

def get_questions_by_category(category):
    try:
        filter_formula = f"{{cname}}='{category}'"
        questions = st.session_state["airtable_questions"].get_all(formula=filter_formula)
        return questions
    except Exception as e:
        print("Error:", e)
        return None
    
def displayTab(tabsVar, tabNo, selected_category):
    with tabsVar:
        questions = get_questions_by_category(selected_category[tabNo])
        if questions:
            tabsVar.markdown(f"# Questions for {selected_category[tabNo]}")
            selected_question = tabsVar.selectbox(
                "Select a question",
                [question["fields"]["qname"] for question in questions],
            )
            selected_question_index = [
                question["fields"]["qname"] for question in questions
            ].index(selected_question)
            st.markdown(f"# {selected_question}")
            st.markdown("**Description**")
            st.markdown(f"{questions[selected_question_index]['fields']['qdesc']}")
            text = questions[selected_question_index]['fields']['qexample'].split("=====")
            i=0
            while text:
                st.markdown(f"**Example {i+1}**")
                st.code(text.pop(0))
                st.markdown("**Explanation**")
                st.markdown("```\n"+text.pop(0)+"\n```")
                i+=1
            
        else:
            st.sidebar.warning("**No questions available**")
def python_code():
    your_code_string = "# Write you code here"
    response_dict = code_editor(your_code_string,
                                height=[20, 30],
                                shortcuts="vscode",
                                focus=True,
                                theme="vs-dark",
                                buttons=custom_btns,
                                key="my_editor",
                                allow_reset=True,
                                lang='python')
    print(response_dict)
    if response_dict['text']!=your_code_string:
        with st.spinner("Running your code..."):
            with open("temp.py", "w") as f:
                f.write(response_dict['text'])
            os.system("python temp.py > tempCode/output.txt")
            with open("output.txt", "r") as f:
                output = f.read()
            st.write(output)
def java_code():
    your_code_string = "// Write you code here"
    response_dict = code_editor(your_code_string,
                                height=[20, 30],
                                shortcuts="vscode",
                                focus=True,
                                theme="vs-dark",
                                buttons=custom_btns,
                                key="my_editor",
                                allow_reset=True,
                                lang='java')
    print(response_dict)
    if response_dict['text']!=your_code_string:
        with st.spinner("Running your code..."):
            with open("Temp.java", "w") as f:
                f.write(response_dict['text'])
            os.system("javac Temp.java > output.txt")
            os.system("java temp > output.txt")
            with open("output.txt", "r") as f:
                output = f.read()
            st.write(output)

def practice_page():
    st.sidebar.markdown("""
        <style>
        .big-font {
            font-size:50px !important;
            font-weight: 600 !important;
            color: #ec5a53;
        }
        </style>
        <div class='big-font'>
            Topics
        </div>
        """, unsafe_allow_html=True)
    categories = st.session_state["categories"]
    arr,tree,string,linkedList = st.sidebar.tabs(categories)
    displayTab(arr, 0, categories)
    displayTab(tree, 1, categories)
    displayTab(string, 2, categories)
    displayTab(linkedList, 3, categories)

    code, chat = st.tabs(["**Solve**", "**CodeX**"])
    
    with code:
        lang=st.selectbox("Select a language", ["Python", "C++", "Java"])
        
        if lang == "Python":
            python_code()
        elif lang == "C++":
            pass
        elif lang == "Java":
            java_code()
    with chat:
            st_app.mainGPT(st.session_state["assistant_id"], st.session_state["thread_id"], 
                           st.session_state["client"], st.session_state["model"], st.session_state["audio"])
practice_page()
            
