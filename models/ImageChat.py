import os
import joblib
import streamlit as st
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

def gemini_image_chat():
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # Function to get response from the Gemini model
    def get_gemini_response(user_input, image):
        model = genai.GenerativeModel('gemini-1.5-flash')
        if user_input:
            response = model.generate_content([user_input, image])
        else:
            response = model.generate_content(image)
        return response.text

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    MODEL_ROLE = 'ai'
    AI_AVATAR_ICON = '✨'

    # Define the data directory
    data_dir = 'data/imagechat'
    images_dir = os.path.join(data_dir, 'images')

    # Create data/ and data/images/ folders if they don't already exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    # Load past chats (if available)
    past_chats_file = os.path.join(data_dir, 'past_chats_list')
    try:
        past_chats = joblib.load(past_chats_file)
    except FileNotFoundError:
        past_chats = {}

    # Sidebar allows a list of past chats and new chat button
    with st.sidebar:


        # Handle "New Chat" button separately
        if st.button('New Chat'):
            st.session_state.current_time = current_time
            st.session_state.chat_title = f'ChatSession-{st.session_state.current_time}'
            st.session_state.messages = []
            st.session_state.gemini_history = []
            past_chats[st.session_state.current_time] = st.session_state.chat_title
            joblib.dump(past_chats, past_chats_file)
            st.rerun()
        st.write('# Previous Chats 👇')
        # Display past chats as a dropdown
        if st.session_state.get('current_time') is None:
            st.session_state.current_time = st.selectbox(
                label='Chat History',
                options=list(past_chats.keys()),
                format_func=lambda x: past_chats.get(x, 'New Chat'),
                placeholder='Select or click "New Chat"',
            )
        else:
            st.session_state.current_time = st.selectbox(
                label='Pick a past chat',
                options=[st.session_state.current_time] + list(past_chats.keys()),
                format_func=lambda x: past_chats.get(x,
                                                     'New Chat' if x != st.session_state.current_time else st.session_state.chat_title),
                placeholder='Select or click "New Chat"',
            )
            st.markdown(f"Selected: {st.session_state.current_time}")

        # Save selected chat title
        st.session_state.chat_title = f'ChatSession-{st.session_state.current_time}'

        # Buttons to clear chat history and delete all chats in one row
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Delete this Chat'):
                if st.session_state.current_time in past_chats:
                    del past_chats[st.session_state.current_time]
                    joblib.dump(past_chats, past_chats_file)
                st_messages_file = os.path.join(data_dir, f'{st.session_state.current_time}-st_messages')
                gemini_messages_file = os.path.join(data_dir, f'{st.session_state.current_time}-gemini_messages')
                if os.path.exists(st_messages_file):
                    os.remove(st_messages_file)
                if os.path.exists(gemini_messages_file):
                    os.remove(gemini_messages_file)
                st.session_state.messages = []
                st.session_state.gemini_history = []
                st.session_state.current_time = None
                st.rerun()

        with col2:
            if st.button('Delete All Chats'):
                for chat_id in list(past_chats.keys()):
                    st_messages_file = os.path.join(data_dir, f'{chat_id}-st_messages')
                    gemini_messages_file = os.path.join(data_dir, f'{chat_id}-gemini_messages')
                    if os.path.exists(st_messages_file):
                        os.remove(st_messages_file)
                    if os.path.exists(gemini_messages_file):
                        os.remove(gemini_messages_file)
                past_chats.clear()
                joblib.dump(past_chats, past_chats_file)
                st.session_state.messages = []
                st.session_state.gemini_history = []
                st.session_state.current_time = None
                st.rerun()

    st.header("Chat with Image using Gemini🖼️", divider="rainbow", anchor=False)

    # Load chat history if available
    try:
        st.session_state.messages = joblib.load(
            os.path.join(data_dir, f'{st.session_state.current_time}-st_messages')
        )
        st.session_state.gemini_history = joblib.load(
            os.path.join(data_dir, f'{st.session_state.current_time}-gemini_messages')
        )
    except FileNotFoundError:
        st.session_state.messages = []
        st.session_state.gemini_history = []

    # # Display chat messages from history on app rerun
    # for message in st.session_state.messages:
    #     with st.chat_message(
    #             name=message['role'],
    #             avatar=message.get('avatar'),
    #     ):
    #         st.markdown(message['content'])
    #         if 'image_path' in message:
    #             image = Image.open(message['image_path'])
    #             st.image(image, caption="Uploaded Image.", use_column_width=True)

    # Input prompt
    input_text = st.chat_input("Input Prompt:", key="input_text")

    # Sidebar for image upload
    with st.sidebar:
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])
        image = None
        image_path = None
        if uploaded_file:
            image = Image.open(uploaded_file)
            if image.format == 'WEBP':
                image = image.convert("RGB")
            #st.image(image, caption="Uploaded Image.", use_column_width=True)
            file_extension = image.format.lower() if image.format else 'jpg'
            image_path = os.path.join(images_dir, f'{st.session_state.current_time}-image.{file_extension}')
            image.save(image_path)

        submit = st.button("Tell me about the image")
    col1, col2 = st.columns(2)
    with col1:
        if image:
            st.image(image, caption="Uploaded Image", width=450)
    # Generate response when submit button is clicked
    if submit and (input_text or image):
        if image and not input_text:
            input_text = "No prompt provided."
        response = get_gemini_response(input_text, image) if image else "No image provided."
        st.subheader("👇 Brief Description of the Image", divider="grey")
        st.write(response)

        # Add user message and response to chat history
        st.session_state.messages.append(
            dict(
                role='user',
                content=f"Prompt: {input_text}\nImage: {uploaded_file.name}",
                image_path=image_path
            )
        )
        st.session_state.messages.append(
            dict(
                role=MODEL_ROLE,
                content=response,
                avatar=AI_AVATAR_ICON,
            )
        )
        st.session_state.gemini_history.append(
            {"user": f"Prompt: {input_text}\nImage: {uploaded_file.name}", "ai": response}
        )

        # Save chat history to files
        joblib.dump(
            st.session_state.messages,
            os.path.join(data_dir, f'{st.session_state.current_time}-st_messages'),
        )
        joblib.dump(
            st.session_state.gemini_history,
            os.path.join(data_dir, f'{st.session_state.current_time}-gemini_messages'),
        )
    elif input_text and image:
        response = get_gemini_response(input_text, image)
        st.write(response)
        # Add user message and response to chat history
        st.session_state.messages.append(
            dict(
                role='user',
                content=f"Prompt: {input_text}\nImage: {uploaded_file.name}",
                image_path=image_path
            )
        )
        st.session_state.messages.append(
            dict(
                role=MODEL_ROLE,
                content=response,
                avatar=AI_AVATAR_ICON,
            )
        )
        st.session_state.gemini_history.append(
            {"user": f"Prompt: {input_text}\nImage: {uploaded_file.name}", "ai": response}
        )

        # Save chat history to files
        joblib.dump(
            st.session_state.messages,
            os.path.join(data_dir, f'{st.session_state.current_time}-st_messages'),
        )
        joblib.dump(
            st.session_state.gemini_history,
            os.path.join(data_dir, f'{st.session_state.current_time}-gemini_messages'),
        )
