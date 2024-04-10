import streamlit as st
import time
import io
from PIL import Image
import pyaudio
import wave
import numpy as np
import threading
from streamlit_extras.stylable_container import stylable_container
import os
import random
from streamlit_card import card
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "file.wav"
def record_audio(filename, stop_event):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    st.session_state['recording'] = True
    frames = []

    while not stop_event.is_set():
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def transcribe_audio(filename, model):
    result = model.transcribe(filename)
    return result["text"]

def generate(prompt, client, botName, question=""):
    print(question)
    with st.spinner("Generating response..."):
        response = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-0125:personal:hrbotfinal:94rYXqzX",
            messages=[
                {"role": "system", "content": f"You are a Human Resources(HR) Interviewer Bot. You are supposed to judge the user's response on attributes like choice of vocabulary, fluency, flow, confidence etc. and score the user's response out of 10 for the HR Interview questions such as the following.\nHR Question: {question}"}, 
                {"role": "user", "content": f"{prompt}"}
            ]
        )
    full_response = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    with st.chat_message("assistant"):
        st.markdown(f"**{botName}** : {full_response}",unsafe_allow_html=True)
    temp_list = full_response.split("Score: ")
    st.session_state["hr_scores"].append(int(temp_list[1][0]) if len(temp_list) >= 2 else 0)
    st.session_state["hr_avg_score"] = sum(st.session_state["hr_scores"])/len(st.session_state["hr_scores"])
    avg_score = st.session_state["hr_avg_score"]*10.0
    with st.sidebar:
        if avg_score >= 50 and avg_score < 80:
            _ = card(
                        title="You're doing good! Keep it up.",
                        text=f"Your average score is {avg_score}%",
                        styles={
                            "card": {
                                "width": "400px",
                                "height": "250px",
                                "border-radius": "60px",
                                "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                                "bg-color": "#0e1117"
                            },
                            "title": {
                                "color": "#FFFF00",
                                "font-family": "Consolas"
                            },
                            "text": {
                                "font-family": "Consolas"
                            }
                        }
                    )
        elif avg_score >= 80:
            _ = card(
                        title="Excellent!. You're doing great!",
                        text=f"Your average score is {avg_score}%",
                        styles={
                            "card": {
                                "width": "400px",
                                "height": "250px",
                                "border-radius": "60px",
                                "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                                "bg-color": "#0e1117"
                            },
                            "title": {
                                "color": "#7CFC00",
                                "font-family": "Consolas"
                            },
                            "text": {
                                "font-family": "Consolas",
                            }
                        }
                    )
        else:
            _ = card(
                        title="You need to improve.",
                        text=f"Your average score is {avg_score}%",
                        styles={
                            "card": {
                                "width": "400px",
                                "height": "250px",
                                "border-radius": "60px",
                                "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                                "bg-color": "#0e1117"
                            },
                            "title": {
                                "color": "#ff0000",
                                "font-family": "Consolas"
                            },
                            "text": {
                                "font-family": "Consolas",
                            }
                        }
                    )
        feedback = "⦿".join([x+"\n" for x in client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are given the following Question, Answer and Feedback triplet. Return the areas for improvement in the Feedback. Feel free to add any extra points you feel are relevant. You must return the areas for improvement in point wise format. Each point MUST be preceded with a *. Do NOT return anything else.\n HR Question: {question}\nAnswer: {prompt}\n Feedback: {full_response}"},
            ]
        ).choices[0].message.content.split("*")])
        st.markdown(f":green[**You can improve in the following areas:**]\n{feedback}")
    full_response, question = "", ""
    
                
def mainGPT(thread_id, client, model,botName):
    col1, col2 = st.columns([0.3, 0.7])
    with col2:
        st.markdown(f'''
        <style>
        section[data-testid="stSidebar"]{{width: 30% !important; 
                    max-width: 100vw !important; 
                    min-width: 2vw !important;}}
        </style>
        ''',unsafe_allow_html=True)
        st.session_state.start_chat = True
        st.session_state.thread_id = thread_id
        with stylable_container(
            key="combined_container",
            css_styles="""
                {
                    position: fixed;
                    bottom: 50px;
                    width: 42vw;
                    justify-content: space-between;
                }
                """,
        ):
            col1, col2 = st.columns([20,1])
            with col1:
                prompt = st.chat_input("Type your query...", key="prompt")
            with col2:
                mic = st.button("🎙️", key="mic")
                
        with stylable_container(
                key="chat",
                css_styles="""
                    {
                        height: 70%;
                        width: 50%;
                        top: 100px;
                        position:fixed;
                        overflow:scroll;
                    }
                    """,
            ):
            if "hr_scores" not in st.session_state:
                st.session_state["hr_scores"] = []
                st.session_state["hr_avg_score"] = 0.0
                
            if 'recording' not in st.session_state:
                st.session_state['recording'] = False
            if 'stop_event' not in st.session_state or 'record_thread' not in st.session_state:
                st.session_state['stop_event'] = threading.Event()
                st.session_state['record_thread'] = threading.Thread(target=record_audio, args=(WAVE_OUTPUT_FILENAME, st.session_state['stop_event']))
            if "openai_model" not in st.session_state:
                st.session_state.openai_model = "gpt-4-turbo-preview"
            if "messages" not in st.session_state:
                if botName == "CodeX":
                    st.session_state.messages = [{"role": "assistant", "content": f"**{botName}** : Hi! I'm {botName}. What can I help you with?"}]
                elif botName == "HR bot":
                    st.session_state.messages = [{"role": "assistant", "content": f"**{botName}** : Hi! I'm {botName}. Let's get started with the interview."}]
            if "first_q" not in st.session_state:
                print("came inside first q")
                st.session_state["first_q"] = st.session_state["hr_questions"][random.randint(0,99)]
                firstq = st.session_state["first_q"]
                st.session_state.messages.append({"role": "assistant", "content": f"{firstq}"})

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    if "image" in message:
                        st.image(message["image"])
                    else:
                        st.markdown(message["content"])
            if mic:
                if st.session_state['recording']:
                    with st.spinner("Processing..."):
                        st.session_state['stop_event'].set()
                        st.session_state['record_thread'].join()
                        st.session_state['recording'] = False
                        print("Stopped")
                        transcription = str(transcribe_audio(WAVE_OUTPUT_FILENAME, model))
                        st.session_state.messages.append({"role": "user", "content": transcription})
                        with st.chat_message("user"):
                            st.markdown(f"**You** : {transcription}")
                        generate(transcription, client, botName, st.session_state["first_q"] if st.session_state["first_q"] != "No" else st.session_state["hr_q"])
                        st.session_state["first_q"] = "No"
                        st.session_state["hr_q"] = st.session_state["hr_questions"][random.randint(0,99)]
                        question = st.session_state["hr_q"]
                        st.session_state.messages.append({"role": "assistant", "content": f"{question}"})
                        with st.chat_message("assistant"):
                            st.markdown(f"**{botName}** : {question}",unsafe_allow_html=True)
                else:
                    st.session_state['stop_event'].clear()
                    st.session_state['record_thread'] = threading.Thread(target=record_audio, args=(WAVE_OUTPUT_FILENAME, st.session_state['stop_event']))
                    st.session_state['record_thread'].start()
                    st.session_state['recording'] = True

            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(f"**You** : {prompt}")
                
                generate(prompt, client, botName, st.session_state["first_q"] if st.session_state["first_q"] != "No" else st.session_state["hr_q"])
                st.session_state["first_q"] = "No"
                st.session_state["hr_q"] = st.session_state["hr_questions"][random.randint(0,99)]
                question = st.session_state["hr_q"]
                st.session_state.messages.append({"role": "assistant", "content": f"{question}"})
                with st.chat_message("assistant"):
                    st.markdown(f"**{botName}** : {question}",unsafe_allow_html=True)
        mic = None
        prompt = ""