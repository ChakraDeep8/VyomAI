import streamlit as st
from gtts import gTTS, langs
from io import BytesIO
import os
import json
import requests
from groq import Groq
from mtranslate import translate
from streamlit import divider


def text2audio():
    def text2audio_module():
        # Initialize Groq client
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        model = "mixtral-8x7b-32768"

        # Initialize session_state_history if it doesn't exist
        if 'session_state_history' not in st.session_state:
            st.session_state.session_state_history = []

        # Function to query the audio generation API
        def query_meta_audio(prompt, headers):
            API_URL = st.secrets["META_API_KEY"]
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                return response.content
            else:
                st.error(f"Error {response.status_code}: {response.text}")
                return None

        # Function to clear chat history in the session state
        def clear_chat_history():
            st.session_state.session_state_history = []

        # Function to generate audio from a prompt
        def audio_generation(input_prompt):
            headers = {"Authorization": f"Bearer {st.secrets['api_key']}"}
            audio_bytes = query_meta_audio(input_prompt, headers)

            if audio_bytes:
                # Save audio to a local file for inspection
                audio_stream = BytesIO(audio_bytes)
                audio_stream.seek(0)
                st.session_state.session_state_history.append(
                    {"role": "assistant", "content": f"Generated audio based on prompt: {input_prompt}"}
                )
                with st.chat_message("assistant"):
                    st.audio(audio_stream, format="audio/wav")
                    st.download_button(label="Download", data=audio_stream, file_name="audio.wav", mime="audio/wav")
            else:
                st.error("Failed to generate audio.")

        # Generate prompt template
        def template(input):
            return f"Generate a very small prompt for an audio clip based on the keyword(s): {input}"

        # Sidebar options for keyword input
        st.sidebar.markdown("Enter a keyword to generate an audio prompt 👇")
        if prompt := st.sidebar.text_input("Enter keyword for audio prompt..."):
            descriptive_prompt = template(prompt)
            st.session_state.session_state_history.append({"role": "user", "content": descriptive_prompt})

            try:
                chat_completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.session_state_history],
                    max_tokens=100,
                    stream=True
                )
                generated_response = "".join([chunk.choices[0].delta.content for chunk in chat_completion if chunk.choices[0].delta.content])
                st.sidebar.write("Generated Prompt:", generated_response)
                st.session_state.session_state_history.append({"role": "assistant", "content": generated_response})
            except Exception as e:
                st.error(f"Error generating prompt with Groq: {e}")

        # Clear chat history
        if st.sidebar.button('Clear Chat History', on_click=clear_chat_history):
            st.session_state.session_state_history = []

        # Display chat history
        for message in st.session_state.session_state_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Generate audio from a user prompt
        if prompt := st.chat_input("Describe the audio you want"):
            st.session_state.session_state_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(f"You: {prompt}")
            with st.spinner('Generating audio...'):
                audio_generation(prompt)

    def text2speech_module():
        # Load languages dynamically from a JSON file
        languages_path = os.path.join('models', 'res', 'languages.json')
        with open(languages_path, 'r') as file:
            data = json.load(file)

        lang_array = {item['name']: item['iso'] for item in data['languages']}

        st.header("Language Translation + Text-to-Speech",divider="rainbow")
        st.markdown("Translate text to a selected language and generate speech")

        # User input for translation and TTS
        input_text = st.text_area("Enter text to translate and convert to speech:", height=150)
        target_language = st.selectbox("Select target language:", list(lang_array.keys()))

        if st.button("Generate Speech"):
            if input_text:
                translation = translate(input_text, lang_array[target_language])
                st.text_area("Translated Text", translation, height=150)

                if lang_array[target_language] in langs._langs:
                    audio_stream = BytesIO()
                    tts = gTTS(text=translation, lang=lang_array[target_language])
                    tts.write_to_fp(audio_stream)
                    audio_stream.seek(0)

                    # Display audio player and download button
                    st.audio(audio_stream, format="audio/wav")
                    st.download_button(label="Download Audio", data=audio_stream, file_name="translated_speech.wav", mime="audio/wav")
                else:
                    st.warning("Text-to-Speech is not supported in the selected language.")
            else:
                st.warning("Please enter some text to translate.")

    # Sidebar to select module
    option = st.sidebar.selectbox("Select an option", ("Text to Speech", "Text to audio"))

    if option == "Text to Speech":
        text2speech_module()
    else:
        text2audio_module()
