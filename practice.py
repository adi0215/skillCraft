import streamlit as st
from airtable import Airtable
import openai
import time
import st_app
from sandbox import custom_btns
from code_editor import code_editor

BASE_ID = st.secrets['BASE_ID']
API_KEY = st.secrets['API_KEY']
client = openai.OpenAI(api_key=st.secrets['OPENAI_API'])

assistant_id = "asst_yyHIOR8BX2rbgHkRDLmq3W54"  #Default assistant. Do not modofy this value.
thread_id = "thread_wQDeamGZrw3mzy6CIHmghs90"  #Default thread. Do not modofy this value.
CATEGORY_TABLE = "categories"
QUESTIONS_TABLE = "questions"

airtable_categories = Airtable(BASE_ID, CATEGORY_TABLE, api_key=API_KEY)
airtable_questions = Airtable(BASE_ID, QUESTIONS_TABLE, api_key=API_KEY)

def get_categories():
    categories = airtable_categories.get_all()
    return [category['fields']['cname'] for category in categories]

def get_questions_by_category(category):
    try:
        filter_formula = f"{{cname}}='{category}'"
        questions = airtable_questions.get_all(formula=filter_formula)
        return questions
    except Exception as e:
        print("Error:", e)
        return None
    
def displayTab(tabsVar, tabNo, selected_category):
    with tabsVar:
        questions = get_questions_by_category(selected_category[tabNo])

        if questions:
            tabsVar.write(f"Questions for {selected_category[tabNo]}:")
            selected_question = tabsVar.selectbox(
                "Select a question",
                [question["fields"]["qname"] for question in questions],
            )
            selected_question_index = [
                question["fields"]["qname"] for question in questions
            ].index(selected_question)
            st.write(f"Question: {selected_question}")
            st.write(
                f"Description: {questions[selected_question_index]['fields']['qdesc']}"
            )
        else:
            st.sidebar.warning("No questions available.")
def practice_page():
    
    categories = get_categories()
    arr,tree,string,linkedList = st.sidebar.tabs(categories)
    
    displayTab(arr, 0, categories)
    displayTab(tree, 1, categories)
    displayTab(string, 2, categories)
    displayTab(linkedList, 3, categories)

    code, chat = st.tabs(["Code", "Chatbot"])
    with code:
        your_code_string = "Write you code here"
        response_dict = code_editor(your_code_string,
                                    height=[20, 30],
                                    shortcuts="vscode",
                                    focus=True,
                                    buttons=custom_btns)
        print(response_dict)
    with chat:
            st_app.mainGPT()
    

    

practice_page()
