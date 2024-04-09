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

def generate(prompt, client,botName):
    
    with st.spinner("Generating response..."):
        response = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-0125:personal:hrbotfinal:94rYXqzX",
            messages=[
                {"role": "system", "content": "You are a Human Resources(HR) Interviewer Bot. You are supposed to judge the user's response on attributes like choice of vocabulary, fluency, flow, confidence etc. and score the user's response out of 10 for the HR Interview questions such as the following.\nHR Question: What are your greatest professional strengths?"}, 
                {"role": "user", "content": "Well, I, uh... I'm pretty good at... communication and, uh, I'm, like, really organized... I think. Additionally, I've been told that I'm very proactive in resolving misunderstandings and conflicts."}
            ]
        )
    full_response = response.choices[0].message.content
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    with st.chat_message("assistant"):
        st.markdown(f"**{botName}** : {full_response}",unsafe_allow_html=True)
    full_response = ""
                
def mainGPT(thread_id, client, model,botName):
    #st.set_page_config(layout="wide")
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
                st.session_state.messages = [{"role": "assistant", "content": f"**{botName}** : Hi! I'm {botName}. Shall we start the interview?"}]
            elif botName == 'AptiBot':
                st.session_state.messages = [{"role": "assistant", "content": f"**{botName}** : Hi! I'm {botName}. I can help you with aptitude questions. Please select a category from the sidebar."}]
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
                    generate(transcription, client,botName)
            else:
                st.session_state['stop_event'].clear()
                st.session_state['record_thread'] = threading.Thread(target=record_audio, args=(WAVE_OUTPUT_FILENAME, st.session_state['stop_event']))
                st.session_state['record_thread'].start()
                st.session_state['recording'] = True

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"**You** : {prompt}")
            generate(prompt, client,botName)
    mic = None
    prompt = ""