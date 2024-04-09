import streamlit as st
from airtable import Airtable
import st_app as st_app
from sandbox import custom_btns
from code_editor import code_editor
from st_pages import hide_pages
from streamlit_extras.stylable_container import stylable_container
from session_states import init_assistant
import os
import json

hide_pages(['Intro'])
hide_pages(['Code'])
hide_pages(['HR'])


global selQuest
selQuest=None

init_assistant()
st.session_state["assistant_id"] = "asst_yyHIOR8BX2rbgHkRDLmq3W54"
st.session_state["botName"]="CodeX"
def get_questions_by_category(category):
    try:
        filter_formula = f"{{cname}}='{category}'"
        questions = st.session_state["airtable_questions"].get_all(formula=filter_formula)
        return questions
    except Exception as e:
        print("Error:", e)
        return None
    
def displayTab(tabsVar, tabNo, selected_category):
    global selQuest  # Declare selQuest as global
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
            
            selQuest = selected_question  # Set the global variable
            print(selQuest,"dispsel")
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


def retrieve_test_cases_from_json(question_name):
    try:
        # Load test cases from JSON file
        with open("testcase.json", "r") as f:
            test_cases_data = json.load(f)
        # Check if the question name exists in the JSON data
        if question_name in test_cases_data:
            test_cases = test_cases_data[question_name]
            input_values_list = test_cases["input_values"]
            expected_outputs = test_cases["expected_outputs"]
            return input_values_list, expected_outputs
        else:
            print("Question not found in JSON file.")
            return None, None
    except Exception as e:
        print("Error:", e)
        return None, None


    
    
def parse_test_cases(test_cases_str):
    
    input_values_list = []
    expected_outputs = []

    # Split the test cases string by the "=====" delimiter
    test_cases = test_cases_str.split("=====")

    for test_case in test_cases:
        # Split each test case by the "Input=" and "Output=" delimiters
        input_output = test_case.strip().split("\n")
        input_str = input_output[0].split("Input=")[1].strip()
        output_str = input_output[1].split("Output=")[1].strip()

        # Convert the input string to a list
        input_values = eval(input_str)

        # Append the input values to the input_values_list
        input_values_list.append(input_values)

        # Append the output string to the expected_outputs list
        expected_outputs.append(output_str)

    return input_values_list, expected_outputs
         
def python_code():
    global selQuest
    your_code_string = "# Write you code here"
    response_dict = code_editor(your_code_string,
                                height=[10, 10],
                                shortcuts="vscode",
                                focus=True,
                                theme="vs-dark",
                                buttons=custom_btns,
                                key="my_editor",
                                allow_reset=True,
                                lang='python')
    print(response_dict)
    if response_dict['text'] != your_code_string:
        # Define the input values
        input_values_list = [
            [-1, 0, 1, 2, -1, -4],
          [0, 1, 1],
          [0, 0, 0],
          [2, 0, 4, 5, 9],
          [3, 0, -2, -1, 1, 2]
            # Add more test cases here
        ]

        # # # Retrieve expected outputs from the Airtable database
        expected_outputs = ["{(-1, 0, 1), (-1, -1, 2)}",
          "set()",
          "{(0, 0, 0)}",
          "set()",
          "{(-2, -1, 3), (-1, 0, 1), (-2, 0, 2)}"]
        
        # input_values_list,expected_outputs=retrieve_test_cases_from_json(selQuest)
        # input_values_list,expected_outputs=retrieve_test_cases_from_airtable(selQuest)
        print(selQuest,"selquest")
        # Initialize a list to store the results
        results = []
        # Modify the code to replace the nums list with the input values and execute for each test case
        for i, input_values in enumerate(input_values_list):
            
            code=response_dict['text']
            modified_code = code.replace("nums=[]",f"nums={input_values}")

            # Write the modified code to temp.py file
            with open("temp.py", "w") as f:
                f.write(modified_code)

            # Run the Python script
            os.system("python temp.py > output.txt")

            # Read the output from the file
            with open("output.txt", "r") as f:
                output = f.read()

            # Compare the output with the expected output
            expected_output = expected_outputs[i]
            result = "Accepted" if output.strip() == expected_output else "Rejected"
            results.append((input_values, result, output))

        # Display the results for each test case
        
        with st.expander("Test Results", expanded=True):
            with stylable_container(
                key="expander",
                css_styles="""
                    {
                        max-height: 400px;
                        overflow-y: auto;
                    }
                    """,
            ):
                for i, (input_values, result, output) in enumerate(results, start=1):
                    st.code(f"Test Case {i} Input: {input_values}")
                    st.code(f"Expected output: {expected_outputs[i-1]}")
                    st.code(f"Actual output: {output.strip()}")
                    st.code(result)

# def python_code():
#     global selQuest
#     print(selQuest,"selllllllll")
#     your_code_string = "# Write you code here"
#     response_dict = code_editor(your_code_string,
#                                 height=[10, 10],
#                                 shortcuts="vscode",
#                                 focus=True,
#                                 theme="vs-dark",
#                                 buttons=custom_btns,
#                                 key="my_editor",
#                                 allow_reset=True,
#                                 lang='python')
#     print(response_dict)
#     if response_dict['text'] != your_code_string:
#         # Retrieve test cases for the selected question
#         input_values_list, expected_outputs = retrieve_test_cases_from_json(selQuest)
#         if input_values_list is None or expected_outputs is None:
#             st.error("Failed to retrieve test cases for the selected question.")
#             return

#         # Initialize a list to store the results
#         results = []

#         # Modify the code to replace the nums list with the input values and execute for each test case
#         if input_values_list and expected_outputs:  # Check if lists are not None
#             for i, input_values in enumerate(input_values_list):
#                 code = response_dict['text']
#                 modified_code = code.replace("nums=[]", f"nums={input_values}")

#                 # Write the modified code to temp.py file
#                 with open("temp.py", "w") as f:
#                     f.write(modified_code)

#                 # Run the Python script
#                 os.system("python temp.py > output.txt")

#                 # Read the output from the file
#                 with open("output.txt", "r") as f:
#                     output = f.read()

#                 # Compare the output with the expected output
#                 expected_output = expected_outputs[i]
#                 result = "Accepted" if output.strip() == expected_output else "Rejected"
#                 results.append((input_values, result, output))

#         # Display the results for each test case
#         with st.expander("Test Results", expanded=True):
#             with stylable_container(
#                 key="expander",
#                 css_styles="""
#                     {
#                         max-height: 400px;
#                         overflow-y: auto;
#                     }
#                     """,
#             ):
#                 for i, (input_values, result, output) in enumerate(results, start=1):
#                     st.code(f"Test Case {i} Input: {input_values}")
#                     st.code(f"Expected output: {expected_outputs[i-1]}")
#                     st.code(f"Actual output: {output.strip()}")
#                     st.code(result)


        




    
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
            
