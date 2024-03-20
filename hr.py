import streamlit as st
from airtable import Airtable
import hr_bot as hr_bot
from st_pages import hide_pages
from session_states import init_assistant
from streamlit_extras.stylable_container import stylable_container
init_assistant()
st.set_page_config(
    initial_sidebar_state='collapsed'
)

st.session_state["botName"]="HR bot"
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

def hr_chat():
    st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )
    hide_pages(['Intro'])
    hide_pages(['Code'])
    hide_pages(['HR'])

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
            
