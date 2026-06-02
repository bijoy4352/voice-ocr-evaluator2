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
import difflib

# ---------------------------
# Tesseract Path configuration (Cross-Platform)
# ---------------------------
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
# Text Comparison & Highlighting Logic
# ---------------------------
def highlight_differences(sheet_text, spoken_text):
    """
    Compares sheet text with spoken text and returns a beautiful 
    HTML string highlighting what matches and what is wrong/missing.
    """
    # Clean up text and split into words
    sheet_words = sheet_text.lower().strip().split()
    spoken_words = spoken_text.lower().strip().split()
    
    matcher = difflib.SequenceMatcher(None, sheet_words, spoken_words)
    html_output = []
    
    for opcode, a_start, a_end, b_start, b_end in matcher.get_opcodes():
        if opcode == 'equal':
            # Spoken perfectly matching the sheet
            for word in sheet_words[a_start:a_end]:
                html_output.append(f"<span style='color: #2e7d32; font-weight: bold;'>{word}</span>")
        elif opcode == 'replace':
            # Spoken text is different from what is on the sheet
            for word in sheet_words[a_start:a_end]:
                html_output.append(f"<span style='background-color: #ffcdd2; color: #b71c1c; text-decoration: line-through;' title='Should be'>{word}</span>")
            for word in spoken_words[b_start:b_end]:
                html_output.append(f"<span style='background-color: #ffe0b2; color: #e65100;' title='You said'>{word}</span>")
        elif opcode == 'delete':
            # Words on the sheet that you skipped/forgot to say
            for word in sheet_words[a_start:a_end]:
                html_output.append(f"<span style='background-color: #cfd8dc; color: #37474f; border-bottom: 2px dashed red;' title='Skipped word'>{word}</span>")
        elif opcode == 'insert':
            # Extra words you said that are not on the sheet
            for word in spoken_words[b_start:b_end]:
                html_output.append(f"<span style='background-color: #b3e5fc; color: #01579b;' title='Extra word'>{word}</span>")
                
    return " ".join(html_output)

# ---------------------------
# Streamlit App Layout
# ---------------------------
st.set_page_config(page_title="Sheet + Voice Discrepancy Checker", layout="centered")
st.title("🎯 Sheet vs. Voice Discrepancy Checker")
st.write("Capture your sheet text, read it aloud, and see exactly where mistakes were made!")

# Step 1: Camera Input
st.header("Step 1: Capture Sheet")
uploaded_image = st.camera_input("Take a photo of the sheet text")

ocr_text = ""
if uploaded_image:
    img = Image.open(uploaded_image)
    img_array = np.array(img)
    ocr_text = pytesseract.image_to_string(img_array).strip()
    
    with st.expander("🔍 View Raw Extracted Sheet Text"):
        st.text_area("OCR Text", ocr_text, height=150)
    speak("Sheet captured successfully. Please record your voice now.")

# Step 2: Voice Input
if ocr_text:
    st.header("Step 2: Record Your Reading")
    recorded_audio = st.audio_input("Click to record yourself reading the text above")
    
    if recorded_audio is not None:
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(recorded_audio) as source:
                audio_data = recognizer.record(source)
                voice_text = recognizer.recognize_google(audio_data).strip()
                
                st.subheader("🎤 What you said:")
                st.write(f'"{voice_text}"')
                
                # Step 3: Compare and Highlight Errors
                st.header("Step 3: Discrepancy Analysis")
                highlighted_html = highlight_differences(ocr_text, voice_text)
                
                # Render the colored HTML blocks safely
                st.markdown("### 📊 Live Evaluation:")
                st.markdown(
                    f"<div style='line-height: 2; font-size: 1.2rem; padding: 15px; border-radius: 5px; border: 1px solid #ddd;'>{highlighted_html}</div>", 
                    unsafe_allow_html=True
                )
                
                # Legend instructions
                st.markdown("""
                **Legend:**
                * <span style='color: #2e7d32; font-weight: bold;'>Green</span> = Read Correctly
                * <span style='background-color: #ffcdd2; color: #b71c1c; text-decoration: line-through;'>Red / Strikethrough</span> = Misread sheet words
                * <span style='background-color: #ffe0b2; color: #e65100;'>Orange</span> = Your mispronounced/substituted voice replacement
                * <span style='background-color: #cfd8dc; color: #37474f; border-bottom: 2px dashed red;'>Grey dashed</span> = Words you skipped entirely
                """, unsafe_allow_html=True)
                
                speak("Analysis
