import os
import streamlit as st
from typing import Generator
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv

def chat_groq():
    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def icon(emoji: str):
        """Shows an emoji as a Notion-style page icon."""
        st.write(
            f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
            unsafe_allow_html=True,
        )

    # Initialize session state for username and unique user ID
    if "username" not in st.session_state:
        st.session_state.username = "DefaultUser"  # Set a default username or retrieve dynamically
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"{st.session_state.username}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    # Unique session initialization
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
  
    st.header("Chat App 🗪", divider="rainbow", anchor=False)
    st.markdown("**Powered by Groq**")

    # Define available models
    models = {
        "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
        "Gemma2-9b-it": {"name": "Gemma2-9b-it", "tokens": 8192, "developer": "Google"},
        "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
    }

    # Model selection and tokens slider
    col1, col2 = st.columns(2)
    with col1:
        model_option = st.selectbox(
            "Choose a model:",
            options=list(models.keys()),
            format_func=lambda x: models[x]["name"],
            index=2
        )

    if st.session_state.selected_model != model_option:
        st.session_state.messages = []
        st.session_state.selected_model = model_option

    max_tokens_range = models[model_option]["tokens"]
    with col2:
        max_tokens = st.slider(
            "Max Tokens:",
            min_value=512,
            max_value=max_tokens_range,
            value=min(32768, max_tokens_range),
            step=512,
            help=f"Adjust max tokens for response. Max: {max_tokens_range}"
        )

    # Display chat history with avatars
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Define response generator function
    def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
        for chunk in chat_completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # Process user input and generate response
    if prompt := st.chat_input("Enter your prompt here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar='👨‍💻'):
            st.markdown(prompt)

        try:
            chat_completion = client.chat.completions.create(
                model=model_option,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                max_tokens=max_tokens,
                stream=True
            )

            # Stream and display response
            with st.chat_message("assistant", avatar="🤖"):
                chat_responses_generator = generate_chat_responses(chat_completion)
                full_response = st.write_stream(chat_responses_generator)

        except Exception as e:
            st.error(f"Error: {e}")

        # Append response to session state messages
        if isinstance(full_response, str):
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            combined_response = "\n".join(str(item) for item in full_response)
            st.session_state.messages.append({"role": "assistant", "content": combined_response})
