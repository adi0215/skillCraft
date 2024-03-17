import streamlit as st
from airtable import Airtable
import openai
import st_app as st_app
from sandbox import custom_btns
from code_editor import code_editor
from st_pages import hide_pages
from streamlit_extras.stylable_container import stylable_container
from session_states import init_assistant
import os


BASE_ID = "appQUrbees7orvriu"
API_KEY = "patsJioGGlyzjX95s.9470d22630e0e2729f0cc9b2a5ef20f741741e5fa35f8b6093c48ec2339552e2"
COMP = 'company'

airtable = Airtable(BASE_ID, COMP, api_key=API_KEY)
# Initialize Streamlit and other components
hide_pages(['Intro'])
hide_pages(['Code'])
hide_pages(['HR'])
init_assistant()
st.session_state["assistant_id"] = "asst_yyHIOR8BX2rbgHkRDLmq3W54"
st.session_state["botName"] = "CodeX"

# Function to retrieve questions by category from Airtable
def get_questions_by_category(category):
    try:
        filter_formula = f"{{cname}}='{category}'"
        questions = st.session_state["airtable_questions"].get_all(formula=filter_formula)
        return questions
    except Exception as e:
        print("Error:", e)
        return None
    
# Function to retrieve questions by category and company from Airtable
def get_questions_by_category_and_company(category,company_name):
    try:
        filter_formula = f"{{compname}}='{company_name}'"
        all_questions = airtable.get_all(formula=filter_formula)
        company_questions = [question for question in all_questions if category in question["fields"]["categories"]]
        return company_questions
    except Exception as e:
        print("Error:", e)
        return None



# Function to display questions in a tab
def displayTab(tabsVar, tabNo, selected_category, selected_company=None):
    with tabsVar:
        if selected_company and selected_company != "None":
            questions = get_questions_by_category_and_company(selected_category[tabNo], selected_company)
        else:
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
            i = 0
            while text:
                st.markdown(f"**Example {i+1}**")
                st.code(text.pop(0))
                st.markdown("**Explanation**")
                st.markdown("```\n"+text.pop(0)+"\n```")
                i += 1
        else:
            st.sidebar.warning("**No questions available**")

# Function to run Python code
def python_code():
    your_code_string = "# Write your code here"
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
    if response_dict['text'] != your_code_string:
        with st.spinner("Running your code..."):
            with open("temp.py", "w") as f:
                f.write(response_dict['text'])
            os.system("python temp.py > output.txt")
            with open("output.txt", "r") as f:
                output = f.read()
            with st.expander("Output"):
                # st.success("Accepted")
                st.code(output)

# Function to run Java code
def java_code():
    your_code_string = "// Write your code here"
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
    if response_dict['text'] != your_code_string:
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

# Main function for the practice page
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
    
    # Dropdown menu for selecting companies
    selected_company = st.sidebar.selectbox("Select a Company", ["None", "Apple", "Microsoft"])

    # Display questions based on the selected company
    if selected_company != "None":
        categories = st.session_state["categories"]
        arr, tree, string, linkedList = st.sidebar.tabs(categories)
        displayTab(arr, 0, categories, selected_company)
        displayTab(tree, 1, categories, selected_company)
        displayTab(string, 2, categories, selected_company)
        displayTab(linkedList, 3, categories, selected_company)
        st.session_state["css_displayed"] = False
        
    else:
        categories = st.session_state["categories"]
        arr, tree, string, linkedList = st.sidebar.tabs(categories)
        displayTab(arr, 0, categories)
        displayTab(tree, 1, categories)
        displayTab(string, 2, categories)
        displayTab(linkedList, 3, categories)
        st.session_state["css_displayed"] = False
    
    # Tabs for code editor and chat
    with stylable_container(
        key="tabs",
        css_styles="""
            {
                position: fixed;
                top: 50px;
                width: 60%;
                justify-content: space-between;
            }
            """,
    ):
        code, chat = st.tabs(["**Solve**", "**CodeX**"])
    
    with code:
        lang = st.selectbox("Select a language", ["Python", "C++", "Java"])
        if lang == "Python":
            python_code()
        elif lang == "C++":
            pass
        elif lang == "Java":
            java_code()
    
    with chat:
        st_app.mainGPT(st.session_state["assistant_id"], st.session_state["thread_id"], 
                       st.session_state["client"], st.session_state["model"], st.session_state["botName"])

# Run the practice page
practice_page()
