import streamlit as st
from code_editor import code_editor
#st.set_page_config(layout='wide')
theme_value = "default"
custom_btns = [
 {
   "name": "Copy",
   "feather": "Copy",
   "alwaysOn": True,
   "commands": ["copyAll"],
   "style": {"top": "0.46rem", "right": "0.4rem"}
 },
 {
   "name": "Shortcuts",
   "feather": "Type",
   "class": "shortcuts-button",
   "hasText": True,
   "commands": ["toggleKeyboardShortcuts"],
   "style": {"bottom": "calc(50% + 1.75rem)", "right": "0.4rem"}
 },
 {
   "name": "Save",
   "feather": "Save",
   "hasText": True,
   "commands": ["save-state", ["response","saved"]],
   "response": "saved",
   "style": {"bottom": "calc(50% - 4.25rem)", "right": "0.4rem"}
 },
 {
   "name": "Run",
   "feather": "Play",
   "primary": True,
   "hasText": True,
   "showWithIcon": True,
   "commands": ["submit"],
   "style": {"bottom": "0.44rem", "right": "0.4rem"}
 },
] #for more buttons https://code-editor-documentation.streamlit.app/Advanced_usage#custom-buttons



def side_bar(sidebarContent):
    for i in sidebarContent:
        st.sidebar.header(str(i))

def left_side(col1,question,explanation,example):
    with col1:
        st.subheader(question)
        st.write(explanation)
        for i in example:
            st.write(i)
    pass

def right_side(col2):
    with col2:
        your_code_string = """Write you code here"""
        response_dict = code_editor(your_code_string,
                                    height=[20, 30],
                                    theme=theme_value,
                                    shortcuts="vscode",
                                    focus=True,
                                    buttons=custom_btns)
        print(response_dict)
    pass


#main remove below stuff to show a demo
def mainSandbox():
  l1=["aaaa","bbbb","cccc"]
  side_bar(l1)

  col1,col2=st.columns([3,5],gap="medium")
  left_side(col1,"quest1",'sbdajdsdvshdsvsfv sfbvdbf sbdajdsdvshdsvsfv sfbvdbf sbdajdsdvshdsvsfv sfbvdbf sbdajdsdvshdsvsfv sfbvdbf sbdajdsd',l1)
  right_side(col2)

