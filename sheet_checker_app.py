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
# Tesseract Path Configuration
# ---------------------------
# Handles local development (Windows) and production (Streamlit Cloud Linux) automatically
if os.path.exists("/usr/bin/tesseract"):
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
else:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ---------------------------
# Helper Function for TTS
# ---------------------------
def speak(text):
    """Generates and plays speech from text via gTTS safely in the cloud."""
    tts = gTTS(text)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    st.audio(mp3_fp, format="audio/mp3")

# ---------------------------
# Text Comparison Logic
# ---------------------------
def highlight_differences(sheet_text, spoken_text):
    """
    Compares the original sheet text with spoken text.
    Returns clean, styled HTML to visually point out mistakes.
    """
    sheet_words = sheet_text.lower().strip().split()
    spoken_words = spoken_text.lower().strip().split()
    
    matcher = difflib.SequenceMatcher(None, sheet_words, spoken_words)
    html_output = []
    
    for opcode, a_start, a_end, b_start, b_end in matcher.get_opcodes():
        if opcode == 'equal':
            # Word read perfectly
            for word in sheet_words[a_start:a_end]:
                html_output.append(f"<span style='color: #2e7d32; font-weight: bold;'>{word}</span>")
        elif opcode == 'replace':
            # Word read incorrectly (Substituted)
            for word in sheet_words[a_start:a_end]:
                html_output.append(f"<span style='background-color: #ffcdd2; color: #b71c1c; text-decoration: line-through;'>{word}</span>")
            for word in spoken_words[b_start:b_end]:
                html_output.append(f"<span style='background-color: #ffe0b2; color: #e65100;'>{word}</span>")
        elif opcode == 'delete':
            # Word skipped completely
            for word in sheet_words[a_start:a_end]:
                html_output.append(f"<span style='background-color: #cfd8dc; color: #37474f; border-bottom: 2px dashed red;'>{word}</span>")
        elif opcode == 'insert':
            # Extra word added that wasn't on the sheet
            for word in spoken_words[b_start:b_end]:
                html_output.append(
