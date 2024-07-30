from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from streamlit_mic_recorder import speech_to_text
from streamlit_TTS import text_to_speech
from gtts.lang import tts_langs
import streamlit as st
import os

langs = tts_langs().keys()

api_key = "AIzaSyBTfA6_lri8MtjYKccTMZ8umT_uvXa6hHU"

chat_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI assistant.Please always respond user query in Pure Urdu language.",
        ),
        ("human", "{human_input}"),
    ]
)

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

chain = chat_template | model | StrOutputParser()


text = speech_to_text(
    language="ur", use_container_width=True, just_once=True, key="STT"
)

if text:
    with st.spinner("Generating Response..."):
        res = chain.invoke({"human_input": text})
        text_to_speech(text=res, language="ur")


else:
    st.error("Could not recognize speech.Please speak again.")
