import streamlit as st
from airtable import Airtable
import apt_bot as apt_bot
from sandbox import custom_btns
from code_editor import code_editor
from st_pages import hide_pages
from streamlit_extras.stylable_container import stylable_container
from session_states import init_assistant, apti_init
import streamlit_book as stb
from streamlit_card import card

hide_pages(['Intro'])
hide_pages(['Code'])
hide_pages(['HR'])
hide_pages(['Aptitude'])
init_assistant()
st.session_state["assistant_id"] = "asst_yyHIOR8BX2rbgHkRDLmq3W54"
st.session_state["botName"]="AptiBot"

def hint_call(q):
    response = st.session_state.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": f"For the given question below. You are supposed to return an appropriate hint. Do NOT answer the question, just give a hint such that it guides the reader to the correct solution. Question : {q}"}
        ]
    )
    return response.choices[0].message.content

def get_questions_by_category(category):
    try:
        filter_formula = f"{{category}}='{category}'"
        questions = st.session_state["aptitude_questions"].get_all(formula=filter_formula)
        return questions
    except Exception as e:
        print("Error:", e)
        return None
def calculate_score(correct,quiz_len):
    if correct:
        st.session_state.player_score += 1
    st.button("Next Question",type="primary",on_click=next_q,args=[quiz_len],key="nextqButton{id}".format(id=st.session_state.current_question),disabled=st.session_state.end_quiz)
def next_q(quiz_len):
    st.session_state.current_question += 1
    if st.session_state.current_question == quiz_len:
        with st.sidebar:
            st.write("Your score is",st.session_state.player_score,"/",quiz_len)
            st.write("Quiz ended")
        st.session_state.end_quiz = True
def displayTab(selected_category):
    if (not st.session_state.end_quiz) or (selected_category not in st.session_state["loaded_apti_categories"].keys()):
        selected_category=str(selected_category)
        if selected_category not in st.session_state["loaded_apti_categories"].keys():
            st.session_state["loaded_apti_categories"]={selected_category:get_questions_by_category(selected_category)}
            apti_init()
        quiz_len = len(st.session_state["loaded_apti_categories"][selected_category])
        if quiz_len:
            st.sidebar.markdown(f"# Questions for {selected_category}")
            ind = st.session_state.current_question
            with st.sidebar:
                question = st.session_state["loaded_apti_categories"][selected_category][ind]
                ans = stb.single_choice(question=question["fields"]["question"],options=[question["fields"]["op1"],question["fields"]["op2"],question["fields"]["op3"],question["fields"]["op4"]],answer_index=question["fields"]["ans_int"])
                if ans[0]:
                    calculate_score(ans[1],quiz_len=quiz_len)
                hint_button = st.button("Hint")
                if hint_button:
                    hint = hint_call(question["fields"]["question"])
                    placeholder = st.empty()
                    with placeholder:
                        st.markdown(f"**:green[Hint: ]**\n{hint}")
                    placeholder = st.empty()
                
    else:
        st.session_state.end_quiz = False
        st.session_state.current_question = 0
        st.session_state.player_score = 0
        st.session_state["loaded_apti_categories"] = {}
        
        return

def apt_chat():
    st.markdown(f'''
    <style>
    section[data-testid="stSidebar"]{{width: 40% !important; 
                max-width: 100vw !important; 
                min-width: 2vw !important;}}
    </style>
    ''',unsafe_allow_html=True)
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

    categories = st.session_state["apti_categories"]
    selectedCategory = st.sidebar.selectbox(label="Topics",options=categories,label_visibility="hidden")
    displayTab(selected_category=selectedCategory)
    st.session_state["css_displayed"] = False
    with stylable_container(
        key="tabs",
        css_styles="""
            {
                position: fixed;
                top: 50px;
                width: 40%;
                justify-content: space-between;
            }
            """,
    ):
     
        apt_bot.mainGPT(st.session_state["apt_assistant_id"], 
            st.session_state["apt_thread_id"], st.session_state["client"], st.session_state["model"], st.session_state["botName"])
apt_chat()
            
