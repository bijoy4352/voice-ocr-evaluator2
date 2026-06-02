# sheet_checker_app.py
import streamlit as st
import cv2
import pytesseract
from PIL import Image
import numpy as np
import pandas as pd
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO

# ---------------------------
# Tesseract path (Windows)
# ---------------------------
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# If deploying online, use: pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ---------------------------
# Helper function for TTS
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

# Voice input
st.subheader("🎤 Voice Input")
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    st.write("Recording 5 seconds...")
    audio_data = recognizer.record(source, duration=5)
    try:
        voice_text = recognizer.recognize_google(audio_data)
        st.write("You said:", voice_text)
        speak(f"You said: {voice_text}")
    except Exception as e:
        st.write("Could not recognize voice.")
        speak("Could not recognize voice.")

# OCR processing
if uploaded_image:
    img = Image.open(uploaded_image)
    img_array = np.array(img)
    ocr_text = pytesseract.image_to_string(img_array)
    st.subheader("📑 OCR Output")
    st.text_area("Extracted Text", ocr_text)

    # Optionally speak the OCR result
    speak("OCR result is ready.")
