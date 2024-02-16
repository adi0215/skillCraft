import openai
import time
import streamlit as st
import io
from PIL import Image
import whisper
import pyaudio
import wave
import numpy as np
import threading
from streamlit_extras.stylable_container import stylable_container

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "file.wav"
client = openai.OpenAI(api_key=st.secrets["OPENAI_API"])   #API KEY
st.set_page_config(layout="wide")
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

def transcribe_audio(filename):
    model = whisper.load_model("small")
    result = model.transcribe(filename)
    return result["text"]

def generate(prompt, assistant_id):
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
                    st.markdown(f"**CodeX** : {full_response}",unsafe_allow_html=True)
                full_response = ""
def mainGPT(): 
    
    assistant_id = "asst_yyHIOR8BX2rbgHkRDLmq3W54"  #Default assistant. Do not modify this value.
    thread_id = "thread_wDXfRFDEMmdiHPSWCMGYQsdp"  #Default thread. Do not modify this value.
    st.session_state.start_chat = True

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    #st.set_page_config(page_title="GPT", page_icon=":robot_face:")
    st.session_state.thread_id = thread_id
    with stylable_container(
            key="button",
            css_styles="""
                {
                    position: fixed;
                    bottom: 50px;
                    padding-left:1010px;
                }
                """,
        ):
        mic = st.button("🎙️")
   
    with stylable_container(
            key="text",
            css_styles="""
                {
                    position: fixed;
                    bottom: 50px;
                    width: 60%;   
                }
                """,
        ):
        prompt = st.chat_input("Type your query...")
    


    #st.title("Chat")
    with stylable_container(
            key="chat",
            css_styles="""
                {
                    height:80%;
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
            st.session_state.messages = [{"role": "assistant", "content": f"**CodeX** : Hi! I'm CodeX. What can I help you with?"}]
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if "image" in message:
                    st.image(message["image"])
                else:
                    st.markdown(message["content"])
    
            
        if mic:
            if st.session_state['recording']:
                st.session_state['stop_event'].set()
                st.session_state['record_thread'].join()
                st.session_state['recording'] = False
                transcription = str(transcribe_audio(WAVE_OUTPUT_FILENAME))
                st.session_state.messages.append({"role": "user", "content": transcription})
                with st.chat_message("user"):
                    st.markdown(f"**You** : {transcription}")
                generate(transcription, assistant_id)
            else:
                st.session_state['stop_event'].clear()
                st.session_state['record_thread'] = threading.Thread(target=record_audio, args=(WAVE_OUTPUT_FILENAME, st.session_state['stop_event']))
                st.session_state['record_thread'].start()
                st.session_state['recording'] = True
                
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(f"**You** : {prompt}")
            generate(prompt, assistant_id)
    mic = None
    prompt = ""