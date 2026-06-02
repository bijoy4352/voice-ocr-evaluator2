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
# Tesseract path
# ---------------------------
# Local Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Cloud deploy: "/usr/bin/tesseract"

# ---------------------------
# Helper TTS function
# ---------------------------
def speak(text):
    tts = gTTS(text)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    st.audio(mp3_fp, format="audio/mp3")

# ---------------------------
# Streamlit Layout
# ---------------------------
st.set_page_config(page_title="Sheet + Voice Evaluator", layout="centered")
st.title("📋 Sheet + Voice Evaluator")

# Step 1: Camera input
st.subheader("Step 1: Capture your sheet")
uploaded_image = st.camera_input("Take a picture of your sheet")

if uploaded_image:
    img = Image.open(uploaded_image)
    img_array = np.array(img)
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # OCR text extraction
    ocr_text = pytesseract.image_to_string(gray)
    ocr_lines = [line.strip() for line in ocr_text.split("\n") if line.strip() != ""]
    st.text_area("OCR Output", "\n".join(ocr_lines))

    # Step 2: Voice input
    st.subheader("Step 2: Record your answers by voice")
    record_voice = st.button("🎤 Record Voice Input")

    if record_voice:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Recording for 5 seconds...")
            audio = recognizer.record(source, duration=5)
        try:
            voice_text = recognizer.recognize_google(audio)
            st.write("You said:", voice_text)
            speak(f"You said: {voice_text}")
            voice_lines = [line.strip() for line in voice_text.split(",") if line.strip() != ""]
        except:
            st.error("Could not recognize voice")
            voice_lines = []

        # Step 3: Evaluate
        st.subheader("Step 3: Evaluation")

        # Load correct answers Excel
        correct_file = st.file_uploader("Upload Correct Answers Excel", type=['xlsx'])
        if correct_file:
            correct_data = pd.read_excel(correct_file)
            correct_list = correct_data['Answer'].astype(str).tolist()

            # Combine OCR + Voice input
            user_input = ocr_lines + voice_lines

            results = []
            correct_count = 0
            for item in user_input:
                if item in correct_list:
                    status = "Correct"
                    correct_count += 1
                else:
                    status = "Wrong"
                results.append({'Item': item, 'Status': status})

            df_results = pd.DataFrame(results)

            # Highlight correct/wrong
            def highlight_status(row):
                return ['background-color: lightgreen' if row.Status == 'Correct' else 'background-color: salmon']*2

            st.dataframe(df_results.style.apply(highlight_status, axis=1))

            # Step 4: Show % correct
            total_items = len(correct_list)
            percentage = (correct_count / total_items) * 100
            st.success(f"You got {percentage:.2f}% correct")
            speak(f"You got {percentage:.2f} percent correct")
