import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages, hide_pages

#page config and structure
st.set_page_config(initial_sidebar_state="collapsed",layout="wide",page_title="SkillCraft",page_icon="🎮") 
#hide the sidebar
st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )
show_pages([
    Page("app.py","Intro"),
    Page("practice.py","Code")
])

hide_pages(['Code'])

#read css file
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#title
st.markdown('<span style="color: aqua;">S</span>kill<span style="color: aqua;">C</span>raft', unsafe_allow_html=True)
st.markdown('<p style="margin-top:10px;font-size:30px;">An LLM powered interview preparation platform</p>',unsafe_allow_html=True)

#scroll down button - doesnt work
b1=st.button('↓', key='scroll_down')


#content buttons
st.header("Content")
with st.container():
    col1, col2, col3 = st.columns(3)
    if col1.button("Code"):
        switch_page('Code')
    col1.progress(0.5, "50%")
    apt= col2.button("Aptitude")
    col2.progress(0.6, "60%")
    code= col3.button("HR")
    col3.progress(0.7, "70%")

