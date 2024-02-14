import streamlit as st
import streamlit.components.v1 as components

# Make Streamlit use the full page width
st.set_page_config(layout="wide")

# Path to your HTML file
html_file_path = 'SkillCraft.html'

# Read the content of the file
with open(html_file_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Display the HTML content in a "maximized" size within Streamlit's constraints
components.html(html_content, height=2000)  # Adjust the height as needed