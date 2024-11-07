import streamlit as st
from gtts import gTTS
from io import BytesIO
import requests
from groq import Groq
from typing import Generator

def text2audio():
    def text2audio_module():
        # Initialize Groq client
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        model = "mixtral-8x7b-32768"

        # Initialize session_state_history if it doesn't exist
        if 'session_state_history' not in st.session_state:
            st.session_state.session_state_history = []

        # Function to query the Hugging Face model for audio generation
        def query_meta_audio(prompt, headers):
            API_URL = st.secrets["META_API_KEY"]
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                return response.content, response.status_code
            else:
                st.write(f"Error: Received status code {response.status_code}")
                st.write(f"Response text: {response.text}")
                return None, response.status_code

        # Function to clear chat history in the session state
        def clear_chat_history():
            st.session_state.session_state_history = []

        # Function to generate audio from a prompt
        def audio_generation(input_prompt):
            api_key = st.secrets["api_key"]
            headers = {"Authorization": f"Bearer {api_key}"}
            audio_bytes, status_code = query_meta_audio(input_prompt, headers)

            if audio_bytes:
                # Save audio to a local file for inspection
                with open("generated_audio.wav", "wb") as audio_file:
                    audio_file.write(audio_bytes)

                try:
                    audio_stream = BytesIO(audio_bytes)  # Convert bytes to an audio stream
                    st.session_state.session_state_history.append(
                        {"role": "assistant", "content": f"Generated audio based on prompt: {input_prompt}"}
                    )
                    with st.chat_message("assistant"):
                        st.audio(audio_stream, format="audio/wav")
                except IOError as e:
                    error_msg = f"IOError: {str(e)}"
                    st.session_state.session_state_history.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.write(error_msg)
            else:
                error_msg = "Failed to generate audio - empty response."
                st.session_state.session_state_history.append({"role": "assistant", "content": error_msg})
                with st.chat_message("assistant"):
                    st.write(error_msg)

        # Template function to format the keyword prompt for Groq
        def template(input):
            prompt = f"Generate a very small prompt for an audio clip based on the keyword(s): {input}"
            return prompt

        # Function to process streaming responses from Groq's completion
        def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
            for chunk in chat_completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        # Sidebar options to enter keywords and generate a descriptive prompt
        st.sidebar.markdown("Use this option to generate descriptive prompt 👇")
        if prompt := st.sidebar.chat_input("Enter keyword for audio prompt..."):
            descriptive_prompt = template(prompt)
            st.session_state.session_state_history.append({"role": "user", "content": descriptive_prompt})

            # Generate a descriptive prompt using Groq
            try:
                chat_completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in
                              st.session_state.session_state_history],
                    max_tokens=100,
                    stream=True
                )
                chat_responses_generator = generate_chat_responses(chat_completion)
                full_response = "".join(list(chat_responses_generator))
                st.sidebar.write("Generated Prompt:", full_response)
                st.session_state.session_state_history.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Error generating prompt with Groq: {e}")

        # Option to clear chat history
        if st.sidebar.button('Clear Chat History', on_click=clear_chat_history):
            st.session_state.session_state_history = []

        # Display existing chat history
        for message in st.session_state.session_state_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Get user input and generate audio if a prompt is provided
        prompt = st.chat_input("Describe the audio you want")
        if prompt:
            st.session_state.session_state_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(f"You: {prompt}")
            with st.spinner('Generating audio...'):
                audio_generation(prompt)
    def text2speech_module():
        text_input = st.text_area("Enter text to convert to speech:")
        language = st.selectbox("Select Language", ("en", "es", "fr", "bn"))
        if st.button("Generate my speech"):
            if text_input:
                tts = gTTS(text=text_input, lang=language)
                audio_stream = BytesIO()
                tts.write_to_fp(audio_stream)
                st.audio(audio_stream, format="audio/wav")
            else:
                st.warning("Please enter some text to convert to speech.")

    option = st.sidebar.selectbox("Select an option", ("Text to Speech", "Text to audio"))

    if option != "Text to audio":
        text2speech_module()

    else:
        text2audio_module()