import streamlit as st
import openai
import os
from pathlib import Path
import tempfile
import time

# Configuration
st.set_page_config(page_title="Live Meeting Assistant", layout="wide")
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Add your key to .streamlit/secrets.toml

# UI Header
st.title("Live Teams Meeting Assistant (Web App)")
st.markdown("Transcribe live audio and ask ChatGPT questions about the ongoing meeting.")

# Audio Upload Section
st.header("1. Upload or Stream Your Audio")
uploaded_audio = st.file_uploader("Upload audio from your virtual microphone", type=["wav", "mp3", "m4a", "webm"])

# Ask a Question
st.header("2. Ask ChatGPT About the Meeting")
user_question = st.text_input("Enter your question")

# Transcription (using OpenAI Whisper API)
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

# Handle audio transcription and question submission
if uploaded_audio and user_question:
    with st.spinner("Transcribing audio..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_audio.read())
            tmp_path = tmp.name
        transcript_text = transcribe_audio(tmp_path)

    prompt = f"""
    You are attending a Microsoft Teams meeting. Here is the live transcript:

    {transcript_text}

    Based on this, please answer the following question:
    {user_question}
    """

    with st.spinner("Thinking..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping someone understand a Teams meeting."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content
            st.success("Response:")
            st.write(answer)
        except Exception as e:
            st.error(f"API Error: {e}")

# Optional: Show transcript
if "transcript_text" in locals():
    if st.checkbox("Show transcript"):
        st.text_area("Transcript", transcript_text, height=300)
