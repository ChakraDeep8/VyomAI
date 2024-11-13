import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import uuid


def audio_spectrogram():
    # Ensure user is logged in
    if 'username' not in st.session_state:
        st.error("You must log in to access this feature.")
        return

    # Generate a unique user ID if it doesn't exist
    if 'user_id' not in st.session_state:
        # Generate a UUID for the session, combining it with the username
        st.session_state.user_id = f"{st.session_state['username']}_{uuid.uuid4()}"

    # Initialize session history if not already done
    if 'session_history' not in st.session_state:
        st.session_state.session_history = []

    # Function to query the Hugging Face model
    def query_audio_model(audio_data):
        try:
            API_URL = st.secrets["AST_API_KEY"]
            headers = {"Authorization": f"Bearer {st.secrets['api_key']}"}
            response = requests.post(API_URL, headers=headers, data=audio_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            st.error(f"Error querying audio model: {err}")
            return None

    # Function to clear chat history
    def clear_chat_history():
        st.session_state.session_history = []
        st.success("Chat history cleared!")

    # Function to save audio data and predictions to session history
    def save_audio_data(audio_filename, predictions, confidences):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        audio_data = {
            "audio_filename": audio_filename,
            "predictions": predictions,
            "confidences": confidences,
            "timestamp": timestamp
        }
        st.session_state.session_history.append(audio_data)

    # UI setup
    st.header("Audio Spectrogram Analysis 🎶")
    st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

    # Sidebar for file upload
    st.sidebar.header("Upload Audio")
    uploaded_audio_file = st.sidebar.file_uploader("Upload an audio file (.wav, .mp3, .flac)",
                                                   type=["wav", "mp3", "flac"])

    # Audio Input using st.audio_input (for direct recording)
    st.write("Record a voice message 🎤")
    audio_value = st.audio_input("Record a voice message")

    # Handle the recorded audio input
    if audio_value:
        st.audio(audio_value, format="audio/wav")  # Play the recorded audio
        st.write("Analyzing recorded audio...")

        # Generate unique filename for the recorded audio
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        audio_filename = f"audio_{timestamp}.wav"

        # Analyze audio using Hugging Face model
        with st.spinner("Analyzing audio..."):
            result = query_audio_model(audio_value)

        # Handle and display results
        if result:
            predictions = [entry.get("label") for entry in result] if isinstance(result, list) else []
            confidences = [entry.get("score") for entry in result] if isinstance(result, list) else []
            save_audio_data(audio_filename, predictions, confidences)

            st.write("Audio analysis result:")
            if predictions and confidences:
                df = pd.DataFrame({"Label": predictions, "Confidence": confidences})
                st.table(df)
        else:
            st.write("Failed to analyze audio.")

    # If file uploaded via sidebar, handle the file upload
    if uploaded_audio_file:
        audio_data = uploaded_audio_file.read()  # Read the uploaded file as bytes
        st.sidebar.audio(audio_data, format=uploaded_audio_file.type)

        # Generate unique filename for the uploaded audio
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        audio_filename = f"audio_{timestamp}.mp3"

        # Analyze audio using Hugging Face model
        with st.spinner("Analyzing uploaded audio..."):
            result = query_audio_model(audio_data)

        # Handle and display results
        if result:
            predictions = [entry.get("label") for entry in result] if isinstance(result, list) else []
            confidences = [entry.get("score") for entry in result] if isinstance(result, list) else []
            save_audio_data(audio_filename, predictions, confidences)

            st.write("Audio analysis result:")
            if predictions and confidences:
                df = pd.DataFrame({"Label": predictions, "Confidence": confidences})
                st.table(df)
        else:
            st.write("Failed to analyze audio.")

    # Display chat history in tabular format
    st.write("### Chat History")
    if st.session_state.session_history:
        chat_data = []
        for message in st.session_state.session_history:
            chat_data.append({
                "Audio Filename": message['audio_filename'],
                "Timestamp": message['timestamp'],
                "Predictions": message['predictions'],
                "Confidence": message['confidences']
            })

        chat_df = pd.DataFrame(chat_data)
        st.table(chat_df)
