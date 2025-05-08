import streamlit as st
import openai
import os
from io import BytesIO
import tempfile
import time
from pydub import AudioSegment
from streamlit_mic_recorder import mic_recorder

# Configuration
st.set_page_config(page_title="Live Meeting Assistant", layout="wide")
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# UI Header
st.title("Live Teams Meeting Assistant (Web App)")
st.markdown("Record your mic, transcribe the meeting, and ask ChatGPT questions about it.")

# Audio Recorder Section
st.header("1. Record Audio from Your Microphone")
audio_bytes = mic_recorder(start_prompt="Click to record", stop_prompt="Stop recording", key="rec")

# Ask a Question
st.header("2. Ask ChatGPT About the Meeting")
user_question = st.text_input("Enter your question")

# Transcription (using OpenAI Whisper API)
def transcribe_audio_bytes(audio_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_data.getvalue())
        tmp_path = tmp.name
    with open(tmp_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

# Handle transcription and GPT response
if audio_bytes and user_question:
    with st.spinner("Transcribing audio..."):
        transcript_text = transcribe_audio_bytes(audio_bytes)

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
