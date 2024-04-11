import streamlit as st
from airtable import Airtable
import st_app as st_app
from sandbox import custom_btns
from code_editor import code_editor
from st_pages import hide_pages
from streamlit_extras.stylable_container import stylable_container
from session_states import init_assistant
import os
import time
import json

hide_pages(['Intro'])
hide_pages(['Code'])
hide_pages(['HR'])
init_assistant()
st.session_state["assistant_id"] = "asst_yyHIOR8BX2rbgHkRDLmq3W54"
st.session_state["botName"]="CodeX"

def code_runner(question, code):
    print(question)
    print(code)
    client = st.session_state["client"]
    code_runner_thread = client.beta.threads.create(
            messages=[
            {
            "role": "user",
            "content": f"Question: {question}\nCode Snippet: {code}"
            }
        ]
    )
    #client.beta.threads.messages.create(
    #    thread_id=st.session_state["code_runner_thread_id"], role="user", content=f"Question: {question}\nCode Snippet: {code}"
    #)
    run = client.beta.threads.runs.create(
        thread_id=code_runner_thread.id,
        assistant_id=st.session_state["code_runner_assistant_id"]
    )

    with st.spinner("Testing your code..."):
        while run.status != "completed":
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=code_runner_thread.id, run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=code_runner_thread.id,
            order="asc"
        )
        assistant_messages_for_run = [
            message
            for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        print(assistant_messages_for_run)
        for message in assistant_messages_for_run:
            if message.file_ids:
                file_id = message.file_ids[0]
                json_file = client.files.retrieve_content(file_id)
                return json.loads(json_file)
        


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
            if "current_question" not in st.session_state:
                st.session_state["current_question"] = questions[selected_question_index]['fields']['qdesc']
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
                                height=[15, 15],
                                shortcuts="vscode",
                                focus=True,
                                theme="vs-dark",
                                buttons=custom_btns,
                                key="my_editor",
                                allow_reset=True,
                                lang='python')
    print(response_dict)
    if response_dict['text']!=your_code_string:
        if "placeholder_1" in st.session_state:
            st.session_state["placeholder_1"].empty()
        with st.spinner("Running your code..."):
            with open("temp.py", "w") as f:
                f.write(response_dict['text'])
            os.system("python temp.py > output.txt")
            with open("output.txt", "r") as f:
                output = f.read()
            with st.expander("Output"):
                # st.success("Accepted")
                st.code(output)
            submit_button = st.button("Submit")
    if submit_button:
        result_json = code_runner(st.session_state["current_question"], response_dict["text"])
        placeholder = st.empty()
        with placeholder:
            testcases = len(result_json)
            passed = 0
            st.markdown(":green[**Results**]")
            for obj in result_json:
                for key, value in obj.items():
                    if key == "Status":
                        st.markdown(f"**{key}**: :green[**{value}**]")
                        if value == "Accepted":
                            passed += 1
                    else:
                        st.markdown(f"**{key}**: {value}")
            st.markdown(f":green[**Test Cases Passed: {passed}/{testcases}**]")
                
        st.session_state["placeholder_1"] = placeholder  #To erase it when another program is run, store the comp and then erase it later
    st.session_state.pop("current_question")
                


    
def java_code():
    your_code_string = "// Write you code here"
    response_dict = code_editor(your_code_string,
                                height=[15, 15],
                                shortcuts="vscode",
                                focus=True,
                                theme="vs-dark",
                                buttons=custom_btns,
                                key="my_editor",
                                allow_reset=True,
                                lang='java')
    print(response_dict)
    if response_dict['text']!=your_code_string:
        if "placeholder_2" in st.session_state:
            st.session_state["placeholder_2"].empty()
        with st.spinner("Running your code..."):
            with open("Temp.java", "w") as f:
                f.write(response_dict['text'])
            os.system("javac Temp.java > output.txt")
            os.system("java temp > output.txt")
            with open("output.txt", "r") as f:
                output = f.read()
            with st.expander("Output"):
                # st.success("Accepted")
                st.code(output)
            submit_button = st.button("Submit")
    if submit_button:
        result_json = code_runner(st.session_state["current_question"], response_dict["text"])
        placeholder = st.empty()
        with placeholder:
            testcases = len(result_json)
            passed = 0
            st.markdown(":green[**Results**]")
            for key, value in result_json.items():
                if key == "Status":
                    st.markdown(f"**{key}**: :green[**{value}**]") if value == "Accepted" else st.markdown(f"**{key}**: :red[**{value}**]")
                    if value == "Accepted":
                        passed += 1
                else:
                    st.markdown(f"**{key}**: {value}")
            st.markdown(f":green[**Test Cases Passed: {passed}/{testcases}**]")
                
        st.session_state["placeholder_1"] = placeholder  #To erase it when another program is run, store the comp and then erase it later
    st.session_state.pop("current_question")


def practice_page():
    st.markdown(f'''
    <style>
    section[data-testid="stSidebar"]{{width: 50% !important; 
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

    categories = st.session_state["categories"]
    arr,tree,string,linkedList = st.sidebar.tabs(categories)
    displayTab(arr, 0, categories)
    displayTab(tree, 1, categories)
    displayTab(string, 2, categories)
    displayTab(linkedList, 3, categories)
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
     
        code, chat = st.tabs(["**Solve**", "**CodeX**"])
 
        with code:
            lang=st.selectbox("Select a language", ["Python", "C++","Java"])
            if lang == "Python":
                python_code()
            elif lang == "C++":
                pass
            elif lang == "Java":
                java_code()
        with chat:
                st_app.mainGPT(st.session_state["assistant_id"], st.session_state["thread_id"], 
                            st.session_state["client"], st.session_state["model"],st.session_state["botName"])
practice_page()