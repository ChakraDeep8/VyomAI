import streamlit as st
from streamlit_option_menu import option_menu
from models import GroqChat, ImageChat, PdfChat, Text2Image, Text2Audio, AudioSpectrogram, qr_generator, res
from PIL import Image
import os

path = os.path.join("models/res", "logo.png")
logo = Image.open(path)

# 1=sidebar menu, 2=horizontal menu, 3=horizontal menu w/ custom menu
EXAMPLE_NO = 1
st.set_page_config(page_title="VyomAI", page_icon=logo, layout="wide")
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
with st.sidebar:
    st.image("models/res/yom.png")

def streamlit_menu(example=1):
    if example == 1:
        # 1. as sidebar menu
        with st.sidebar:
            selected = option_menu(
                menu_title="Chat Menu",  # required
                options=["Home", "Image", "Pdf", "Text 👉 Image", "Text 👉  Audio", "Audio Spectrogram", "QR Generator"],  # required
                icons=["house", "camera", "envelope", "sunset", "play", "graph-up", "box"],  # optional
                menu_icon="cast",  # optional
                default_index=0,  # optional
            )
        return selected

    if example == 2:
        # 2. horizontal menu w/o custom style
        selected = option_menu(
            menu_title=None,  # required
            options=["Home", "Projects", "Contact"],  # required
            icons=["house", "book", "envelope"],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
        )
        return selected

    if example == 3:
        # 2. horizontal menu with custom style
        selected = option_menu(
            menu_title=None,  # required
            options=["Home", "Projects", "Contact"],  # required
            icons=["house", "book", "envelope"],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {
                    "font-size": "25px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "green"},
            },
        )
        return selected


selected = streamlit_menu(example=EXAMPLE_NO)

if selected == "Home":
    GroqChat.chat_groq()
if selected == "Image":
    ImageChat.gemini_image_chat()
if selected == "Pdf":
    PdfChat.gemini_pdf_chat()
if selected == "Text 👉 Image":
    Text2Image.gemini_text2image()
if selected == "Text 👉  Audio":
    Text2Audio.text2audio()
if selected == "Audio Spectrogram":
    AudioSpectrogram.audio_spectrogram()
if selected == "QR Generator":
    qr_generator.QR()