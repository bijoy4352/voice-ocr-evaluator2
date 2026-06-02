import streamlit as st
import cv2
import pytesseract
from PIL import Image
import numpy as np
import pandas as pd
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import os

# ---------------------------
# Tesseract Path configuration (Cross-Platform)
# ---------------------------
# Checks if running on Streamlit Cloud (Linux), otherwise falls back to your Windows path
if os.path.exists("/usr/bin/tesseract"):
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
else:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ---------------------------
# Helper function for TTS (Google Text-to-Speech)
# ---------------------------
def speak(text):
    tts = gTTS(text)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    st.audio(mp3_fp, format="audio/mp3")

# ---------------------------
# Streamlit App Layout
# ---------------------------
st.set_page_config(page_title="Sheet + Voice Checker", layout="centered")
st.title("📄 Sheet + Voice Checker App")

# Camera input
uploaded_image = st.camera_input("Capture your sheet")

# Voice input using Browser Audio Recording
st.subheader("🎤 Voice Input")

# st.audio_input leverages the user's browser/device mic correctly in the cloud
recorded_audio = st.audio_input("Record your voice instructions")

if recorded_audio is not None:
    recognizer = sr.Recognizer()
    try:
        # Convert the Streamlit uploaded file into an audio file SpeechRecognition can read
        with sr.AudioFile(recorded_audio) as source:
            audio_data = recognizer.record(source)
            voice_text = recognizer.recognize_google(audio_data)
            
            st.success(f"You said: {voice_text}")
            speak(f"You said: {voice_text}")
    except Exception as e:
        st.error("Could not recognize voice. Try speaking more clearly.")
        speak("Could not recognize voice.")

# OCR processing
if uploaded_image:
    img = Image.open(uploaded_image)
    img_array = np.array(img)
    
    # Process image text
    ocr_text = pytesseract.image_to_string(img_array)
    st.subheader("📑 OCR Output")
    st.text_area("Extracted Text", ocr_text, height=200)

    # Speak the OCR result alert
    speak("OCR result is ready.")
