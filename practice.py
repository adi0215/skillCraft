import streamlit as st
from airtable import Airtable

BASE_ID = "appQUrbees7orvriu"
API_KEY = "patsJioGGlyzjX95s.9470d22630e0e2729f0cc9b2a5ef20f741741e5fa35f8b6093c48ec2339552e2"

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

if __name__ == "__main__":
    practice_page()
