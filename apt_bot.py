import streamlit as st
import time
import io
from PIL import Image
import pyaudio
import wave
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

def generate(prompt, assistant_id, client, botName):
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, role="user", content=prompt
    )
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id
    )

    with st.spinner("Generating response..."):
        while run.status != "completed":
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id,
            order="asc"
        )
        assistant_messages_for_run = [
            message
            for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        print(assistant_messages_for_run)
        if 'images' not in st.session_state:
            st.session_state['images'] = []
        for message in assistant_messages_for_run:
            full_response = ""
            for content in message.content:
                if content.type == "image_file":
                    image_data = client.files.content(content.image_file.file_id)
                    image_data_bytes = image_data.read()
                    image = Image.open(io.BytesIO(image_data_bytes))
                    st.session_state.messages.append({"role": "assistant", "image": image})
                    st.image(image)
                else:
                    full_response += content.text.value
                if full_response:
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                with st.chat_message("assistant"):
                    st.markdown(f"**AptBot** : {full_response}",unsafe_allow_html=True)
                full_response = ""
                
def mainGPT(assistant_id, thread_id, client, model, botName):
    #st.set_page_config(layout="wide")
    st.session_state.start_chat = True
    st.session_state.thread_id = thread_id
    with stylable_container(
        key="combined_container",
        css_styles="""
            {
                position: fixed;
                bottom: 50px;
                width: 50vw;
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
                st.session_state.messages = [{"role": "assistant", "content": f"**AptBot** : Hi! I'm AptBot. I can help you with Aptitude Questions. Please let me know if you require help with anyhting!"}]
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
                    generate(transcription, assistant_id, client,botName)
            else:
                st.session_state['stop_event'].clear()
                st.session_state['record_thread'] = threading.Thread(target=record_audio, args=(WAVE_OUTPUT_FILENAME, st.session_state['stop_event']))
                st.session_state['record_thread'].start()
                st.session_state['recording'] = True

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"**You** : {prompt}")
            generate(prompt, assistant_id, client, botName)
    mic = None
    prompt = ""