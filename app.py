import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages, hide_pages
from session_states import init_assistant
from signup import user_signup
from login import user_login
from streamlit_lottie import st_lottie
import json
import streamlit_shadcn_ui as ui
from streamlit_oauth import OAuth2Component
import base64

def load_lottie_anim(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

st.set_page_config(initial_sidebar_state="auto", layout='wide',page_title="SkillCraft",page_icon="🎮")
#hide sidebar
init_assistant()
# Buttons for login and signup
st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)


st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )
show_pages([
    Page("app.py","Intro"),
    Page("practice.py","Code"),
    Page("hr.py","HR")
])

hide_pages(['Code'])
hide_pages(['HR'])

#read css file
print(st.session_state["css_displayed"] if "css_displayed" in st.session_state else "First run")
if "css_displayed" not in st.session_state or st.session_state["css_displayed"] == False:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        st.session_state["css_displayed"] = True
    st.markdown('<span style="color: aqua;">S</span>kill<span style="color: aqua;">C</span>raft', unsafe_allow_html=True)
    st.markdown('<p style="margin-top:10px;font-size:30px;">An LLM powered interview preparation platform</p>',unsafe_allow_html=True)
#scroll down button - doesnt work
st.write("")
st.write("")
with st.container():
    col_1, col_2 = st.columns([0.4, 0.6])
    with col_2:
        #loginbtn = ui.button(
        #                       text="Login",
        #                       className="bg-[#0e1117] text-green-500 hover-green-900 border border-green rounded-full"
        #                    )
        #if loginbtn:
        CLIENT_ID = "218771962086-l8l3mdddho887uob5g1it04e7tsu6305.apps.googleusercontent.com"
        CLIENT_SECRET = "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"
        REDIRECT_URI = "http://localhost:8501"
        AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
        TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
        REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"

        if "auth" not in st.session_state:
            # create a button to start the OAuth2 flow
            oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)
            
            result = oauth2.authorize_button(
                name="Log in with Google",
                icon="https://www.google.com.tw/favicon.ico",
                redirect_uri=REDIRECT_URI,
                scope="openid email profile",
                key="google",
                extras_params={"prompt": "consent", "access_type": "offline"},
                use_container_width=False,
                pkce='S256',
            )
            
            if result:
                st.write(result)
                # decode the id_token jwt and get the user's email address
                id_token = result["token"]["id_token"]
                # verify the signature is an optional step for security
                payload = id_token.split(".")[1]
                # add padding to the payload if needed
                payload += "=" * (-len(payload) % 4)
                payload = json.loads(base64.b64decode(payload))
                email = payload["email"]
                st.session_state["auth"] = email
                st.session_state["token"] = result["token"]
                st.rerun()
        else:
            st.write("You are logged in!")
            #st.write(st.session_state["auth"])
            #st.write(st.session_state["token"])
            logoutbtn = ui.button(
                                text="Logout",
                                className="bg-[#0e1117] text-cyan-500 hover-green-900 border border-green rounded-full"
                            )
            if logoutbtn:
                del st.session_state["auth"]
                del st.session_state["token"]
            #user_login()

    #with col_2:
    #    signupbtn = ui.button(
    #                            text="Sign ",
    #                            className="bg-[#0e1117] text-cyan-500 hover-green-900 border border-green rounded-full"
    #                       )
    #    if signupbtn:
    #        user_signup()


with st.container():
    ccol1, ccol2 = st.columns([0.35, 0.75])
    with ccol1:
        st_lottie(
        load_lottie_anim("coding1.json"),
        loop=True,
        quality="high",
        height=400,
        width=400       
    )
    with ccol2:
        st.write("")
        st.write("")
        st.markdown("""
        <div style="text-align: left; color: #FFFFFF;">
            <h2 style="color: #8F00FF; margin-bottom: 0px;">Code</h2>
            <p style="font-size: large; font-family: 'Consolas', monospace; text-align:left; margin-top:10px;">Unlock the potential of CodeX, your personal coding mentor. From debugging to optimized solutions, CodeX offers tailored advice, efficiency upgrades, and visual explanations for complex concepts. Enhance your code with our interactive interpreter and elevate your programming prowess. Let's code smarter, not harder!.</p>
        </div>
        """, unsafe_allow_html=True)
        print("Came here1")
        codebutton = st.button(":violet[Start Coding..]")
        if codebutton:
            print("Came here2")
            switch_page("Code")
    acol1, acol2 = st.columns([0.35, 0.75])
    with acol1:
        st_lottie(
        load_lottie_anim("aptitude3.json"),
        loop=True,
        quality="high",
        height=400,
        width=400       
    )
    with acol2:
        st.write("")
        st.write("")
        st.write("")
        st.markdown("""
        <div style="text-align: left; color: #FFFFFF;">
            <h2 style="color: #00FFFF; margin-bottom: 0px;">Aptitude</h2>
            <p style="font-size: large; font-family: 'Consolas', monospace; text-align:left; margin-top:10px;">Prepare to tackle any intellectual hurdle with our dynamic aptitude section.\nFrom quantitative reasoning to logical puzzles, our AI-powered platform\noffers personalized practice sessions and detailed explanations to help you\nmaster the art of problem-solving. Start your cognitive enhancement journey with us now!.</p>
        </div>
        """, unsafe_allow_html=True)
        aptbutton = st.button(":blue[Solve..]")
        if aptbutton:
            pass
    hcol1, hcol2 = st.columns([0.35, 0.75])
    with hcol1:
        st_lottie(
            load_lottie_anim("HR1.json"),
            loop=True,
            quality="high",
            height=400,
            width=400       
    )
    with hcol2:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown("""
        <div style="text-align: left; color: #FFFFFF;">
            <h2 style="color: #7CFC00; margin-bottom: 0px;">HR</h2>
            <p style="font-size: large; font-family: 'Consolas', monospace; text-align:left; margin-top:10px;">Ace your HR interviews with confidence. Our custom model, trained on a vast\n HR dataset, analyzes your responses and coaches you towards excellence.\nImprove your vocabulary, polish your language fluency, and communicate with impact.\nLet's refine your answers together and make your next interview your best one yet!.</p>
        </div>
        """, unsafe_allow_html=True)
        hrbutton = st.button(":green[Get Started..]")
        if hrbutton:
            switch_page("HR")