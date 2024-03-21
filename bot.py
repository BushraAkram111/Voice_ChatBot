from itertools import zip_longest
import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import pyttsx3
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import pytesseract

# Install the required libraries
# pip install streamlit pyttsx3 SpeechRecognition pillow pytesseract

st.set_page_config(page_title="AI-ChatBot", layout="wide")

st.title("AI-ChatBot")

# Initialize the ChatOpenAI model
openai_api_key = "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"
chat = ChatOpenAI(
    temperature=0.5,
    model_name="gpt-3.5-turbo",
    openai_api_key=openai_api_key,
    max_tokens=100
)

executor = ThreadPoolExecutor(max_workers=2)

# Initialize Tesseract OCR for image processing
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Change this path to your Tesseract installation

# Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

# Define missing functions
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

def process_image_question(image):
    try:
        # Use Tesseract OCR to extract text from the image
        text = pytesseract.image_to_string(Image.open(image))
        return text
    except Exception as e:
        st.write(f"Error processing image: {e}")
        return "Error processing image"

def build_message_list():
    zipped_messages = [SystemMessage(content="""...[Your initial instruction message]...""")]
    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            if isinstance(human_msg, bytes):
                zipped_messages.append(HumanMessage(content=human_msg.decode('utf-8', 'ignore')))
            else:
                zipped_messages.append(HumanMessage(content=human_msg))
        if ai_msg is not None:
            zipped_messages.append(AIMessage(content=ai_msg))
    return zipped_messages

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Sidebar section
st.sidebar.title("Welcome To AI World")

new_chat_button = st.sidebar.button("New Chat")

if new_chat_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['search_history'] = []

recommended_searches = ["History", "Science", "Technology", "AI", "Machine Learning", "Deep Learning", "NLP"]  # Customize as needed
st.sidebar.title("Recommended Searches")
st.sidebar.write(recommended_searches)

# About Us section
st.sidebar.title("About Us")
st.sidebar.write("This chatbot is designed to provide answers to your queries. "
                 "Ask questions in text, voice, or upload images for more personalized responses.")

# User input section
user_input_type = st.radio("Select input type:", ("Text", "Voice", "Picture"))

if user_input_type == "Text":
    user_input = st.text_input("Enter your question:")
    if st.button("Ask Question"):
        st.session_state.past.append(user_input)
        st.session_state.search_history.append(user_input)
        output = generate_response()
        st.session_state.generated.append(output)
elif user_input_type == "Voice":
    if st.button("Ask Question (Voice)"):
        user_input = capture_audio()
        st.session_state.past.append(user_input)
        st.session_state.search_history.append(user_input)
        output = generate_response()
        st.session_state.generated.append(output)
        text_to_speech(output)
elif user_input_type == "Picture":
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image is not None:
        # Display the uploaded image
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        # Process image and generate response
        user_input = process_image_question(uploaded_image)
        st.session_state.past.append(user_input)
        st.session_state.search_history.append(user_input)
        output = generate_response()
        st.session_state.generated.append(output)

# Display the conversation
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

# Sidebar footer
st.sidebar.markdown("***")
st.sidebar.text("Created by Bushra Akram")
