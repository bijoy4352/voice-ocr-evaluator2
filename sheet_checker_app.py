# sheet_checker_app.py
import streamlit as st
import cv2
import pytesseract
from PIL import Image
import numpy as np
import pandas as pd
import speech_recognition as sr
import pyttsx3

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

engine = pyttsx3.init()

st.set_page_config(page_title="Sheet + Voice Checker", layout="centered")
st.title("📋 Sheet + Voice Checker App")

uploaded_image = st.camera_input("Capture your sheet")
correct_file = st.file_uploader("Upload correct answers Excel", type=['xlsx'])

if uploaded_image and correct_file:
    img = np.array(Image.open(uploaded_image))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ocr_text = pytesseract.image_to_string(gray)
    ocr_lines = [line.strip() for line in ocr_text.split('\n') if line.strip() != '']
    correct_data = pd.read_excel(correct_file)
    correct_list = correct_data['Answer'].astype(str).tolist()
    st.info("Click the button below and start speaking your answers.")

    if st.button("🎤 Start Voice Input"):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            st.write("Listening...")
            audio = recognizer.listen(source, timeout=10)
        try:
            voice_text = recognizer.recognize_google(audio)
            st.write("You said:", voice_text)
            voice_lines = [line.strip() for line in voice_text.split(',') if line.strip() != '']
        except:
            st.error("Voice not recognized")
            voice_lines = []

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
        def highlight_status(row):
            if row.Status == "Correct":
                return ['background-color: lightgreen']*2
            else:
                return ['background-color: salmon']*2
        st.subheader("Comparison Result")
        st.dataframe(df_results.style.apply(highlight_status, axis=1))
        total_items = len(correct_list)
        percentage = (correct_count / total_items) * 100
        st.success(f"✅ You got {percentage:.2f}% correct!")
        engine.say(f"You got {percentage:.2f} percent correct")
        engine.runAndWait()
        df_results.to_excel('comparison_result.xlsx', index=False)
        st.info("📥 Results saved as comparison_result.xlsx")
