from itertools import zip_longest
import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import pyttsx3
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor

st.title(" AI-VoiceBot")


openapi_key = st.secrets["OPENAI_API_KEY"]

# Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# Initialize the ChatOpenAI model
chat = ChatOpenAI(
    temperature=0.5,
    model_name="gpt-3.5-turbo",
    openai_api_key=openapi_key, 
    max_tokens=100
)

executor = ThreadPoolExecutor(max_workers=2)

def build_message_list():
    zipped_messages = [SystemMessage(content="""...[Your initial instruction message]...""")]
    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(content=human_msg))
        if ai_msg is not None:
            zipped_messages.append(AIMessage(content=ai_msg))
    return zipped_messages

def generate_response():
    try:
        zipped_messages = build_message_list()
        ai_response = chat(zipped_messages)
        return ai_response.content
    except Exception as e:
        st.write(f"Error: {e}")
        return "Error generating response"
    
def capture_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        st.warning("Please hold! Loading response...")
        return ""
    except sr.RequestError:
        st.error("API unavailable. Please check your internet connection and try again.")
        return ""


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if st.button("Ask Question?"):
    user_input = capture_audio()
    st.session_state.past.append(user_input)
    output = generate_response()
    st.session_state.generated.append(output)
    text_to_speech(output)
    
    # Reset the button state
    st.experimental_rerun()

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
