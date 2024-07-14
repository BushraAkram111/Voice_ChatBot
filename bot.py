from itertools import zip_longest
import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import pyttsx3
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor

# Set page configuration
st.set_page_config(page_title="AI VoiceBot", layout="wide")

# Sidebar for API Key
with st.sidebar:
    st.header("Chatbot Settings")
    user_openai_api_key = st.text_input("Enter your OpenAI API Key (optional):", type="password", placeholder="Your API Key Here")

# Main Area
st.title("AI-VoiceBot")

# Default OpenAI API Key (Set your own default key here)
DEFAULT_OPENAI_API_KEY = "YOUR_DEFAULT_OPENAI_API_KEY"

# Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

executor = ThreadPoolExecutor(max_workers=2)

def build_message_list():
    zipped_messages = [SystemMessage(content="You are a helpful assistant. Answer the user's questions based on the context.")]
    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(content=human_msg))
        if ai_msg is not None:
            zipped_messages.append(AIMessage(content=ai_msg))
    return zipped_messages

def generate_response(api_key):
    try:
        # Initialize the ChatOpenAI model with the provided API key
        chat = ChatOpenAI(
            temperature=0.5,
            model_name="gpt-3.5-turbo",
            openai_api_key=api_key,
            max_tokens=100
        )
        zipped_messages = build_message_list()
        ai_response = chat(zipped_messages)
        return ai_response.content
    except Exception as e:
        return str(e)  # Return error message if any

def capture_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        st.warning("Could not understand audio. Please try again.")
        return ""
    except sr.RequestError:
        st.error("API unavailable. Please check your internet connection and try again.")
        return ""

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Text input field for user questions
user_input_text = st.text_input("Type your question here:")

# Function to handle API key selection and response generation
def handle_question():
    api_key = user_openai_api_key if user_openai_api_key else DEFAULT_OPENAI_API_KEY
    output = generate_response(api_key)
    
    if "Error" in output:
        if user_openai_api_key:
            st.warning("Trying with the provided API Key.")
            output = generate_response(user_openai_api_key)
            if "Error" not in output:
                st.session_state.past.append(user_input_text)
                st.session_state.generated.append(output)
                text_to_speech(output)
                st.experimental_rerun()
            else:
                st.error(f"User's API Key also failed: {output}")
        else:
            st.error(f"Default API Key failed: {output}")
    else:
        st.session_state.past.append(user_input_text)
        st.session_state.generated.append(output)
        text_to_speech(output)
        st.experimental_rerun()

if st.button("Ask Question"):
    if user_input_text:
        handle_question()
    else:
        st.warning("Please type a question.")

# Voice input button
if st.button("Ask Question by Voice"):
    if user_openai_api_key or DEFAULT_OPENAI_API_KEY:
        user_input = capture_audio()
        if user_input:
            st.session_state.past.append(user_input)
            api_key = user_openai_api_key if user_openai_api_key else DEFAULT_OPENAI_API_KEY
            output = generate_response(api_key)
            if "Error" in output:
                if user_openai_api_key:
                    api_key = user_openai_api_key
                    output = generate_response(api_key)
                    if "Error" not in output:
                        st.session_state.generated.append(output)
                        text_to_speech(output)
                        st.experimental_rerun()
                    else:
                        st.error(f"User's API Key also failed: {output}")
                else:
                    st.error(f"Default API Key failed: {output}")
            else:
                st.session_state.generated.append(output)
                text_to_speech(output)
                st.experimental_rerun()
        else:
            st.warning("Could not understand audio. Please try again.")
    else:
        st.error("Please enter your OpenAI API Key or use the default API Key.")

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
