import streamlit as st
from airtable import Airtable
import openai
import time

BASE_ID = "appQUrbees7orvriu"
API_KEY = "patsJioGGlyzjX95s.9470d22630e0e2729f0cc9b2a5ef20f741741e5fa35f8b6093c48ec2339552e2"
client = openai.OpenAI(api_key="")

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

def practice_page():
    categories = get_categories()
    selected_category = st.sidebar.selectbox("Select a category", categories)

    questions = get_questions_by_category(selected_category)

    if questions:
        st.sidebar.write(f"Questions for {selected_category}:")
        selected_question = st.sidebar.selectbox("Select a question", [question['fields']['qname'] for question in questions])
        selected_question_index = [question['fields']['qname'] for question in questions].index(selected_question)
        st.write(f"Question: {selected_question}")
        st.write(f"Description: {questions[selected_question_index]['fields']['qdesc']}")
    else:
        st.sidebar.warning("No questions available.")

    
    st.title("GPT Chatbot")
    st.session_state.start_chat = True

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None


    chat_thread = client.beta.threads.create()
    st.session_state.thread_id = chat_thread.id

    if st.session_state.start_chat:
        if "openai_model" not in st.session_state:
            st.session_state.openai_model = "gpt-4-turbo-preview"
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        if prompt := st.chat_input("Type your query..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"**You :** {prompt}")
            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id, role="user", content=prompt
            )
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions="""You are CodeX. Your primary role is to assist users with coding-related questions, 
                offering precise code completions and programming advice, with a special focus on competitive programming. 
                Your knowledge base will include resources like textbooks on algorithms and data structures, 
                problem sets from competitive programming platforms, comprehensive API documentation for various libraries and frameworks, 
                coding standards and best practices, sample projects and code examples showcasing good practices, and research papers in computer science. 
                You can generate images, including graphs and diagrams, using the built-in code interpreter with libraries such as matplotlib. 
                Your responses should be clear, accurate, and practical, maintaining a professional demeanor focused on coding assistance and educational support. 
                When generating images like digraphs or trees, ensure they represent data correctly and aren't overly fancy. 
                If you are asked to find out errors or generate a snippet to solve a problem, run it on your interpreter and test your solution. 
                When explaining concepts, always make sure to include examples to help demonstrate or visualize the concepts more accurately. 
                For example, If the user asks you to explain DFS with an example, plot a simple undirected graph using matplotlib in your code interpreter, 
                display it and continue with your explanation.""",
            )

            with st.spinner("Generating response..."):
                while run.status != "completed":
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id, run_id=run.id
                    )
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )
                assistant_messages_for_run = [
                    message
                    for message in messages
                    if message.run_id == run.id and message.role == "assistant"
                ]
                print(assistant_messages_for_run)
                for message in assistant_messages_for_run:
                    full_response = ""
                    image_displayed = False
                    for content in message.content:
                        if content.type == "image_file":
                            image_data = client.files.content(content.image_file.file_id)
                            image_data_bytes = image_data.read()
                            image_path = "./my-image.png"
                            with open(image_path, "wb") as file:
                                file.write(image_data_bytes)
                            st.image(image_path)
                            image_displayed = True 
                        else:
                            full_response += content.text.value
                    if image_displayed:
                        st.session_state.messages.append({"role": "assistant", "content": "[Image displayed above]"})
                    if full_response:
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        with st.chat_message("assistant"):
                            st.markdown(f"**GPT** : {full_response}", unsafe_allow_html=True)
