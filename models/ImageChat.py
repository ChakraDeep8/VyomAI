import streamlit as st
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

def gemini_image_chat():
    load_dotenv()
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    # Function to get response from the Gemini model
    def get_gemini_response(user_input, image):
        model = genai.GenerativeModel('gemini-1.5-flash')
        if user_input:
            response = model.generate_content([user_input, image])
        else:
            response = model.generate_content(image)
        return response.text

    # Set session states for user and chat session management
    if 'username' not in st.session_state:
        st.error("You must be logged in to use this feature.")
        return

    username = st.session_state['username']
    unique_chat_id = f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    # Ensure imagechat_messages is initialized as a dictionary
    if "imagechat_messages" not in st.session_state or not isinstance(st.session_state.imagechat_messages, dict):
        st.session_state.imagechat_messages = {}
    if unique_chat_id not in st.session_state.imagechat_messages:
        st.session_state.imagechat_messages[unique_chat_id] = []

    AI_AVATAR_ICON = '✨'

    st.header("Chat with Image using Gemini🖼️", divider="rainbow")

    # Display chat history for the current session
    for msg in st.session_state.imagechat_messages[unique_chat_id]:
        with st.chat_message(msg['role'], avatar="👨‍💻" if msg['role'] == "user" else AI_AVATAR_ICON):
            st.markdown(msg['content'])

    # Input and Image Upload
    input_text = st.chat_input("Input Prompt:", key="input_text")
    uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])

    image = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        if image.format == 'WEBP':
            image = image.convert("RGB")

    # Display the uploaded image
    if image:
        st.image(image, caption="Uploaded Image", width=450)

    # "Tell me more about the image" button logic
    submit = st.sidebar.button("Tell me more about the image")

    # Generate and display response when the button is clicked
    if submit and (input_text or uploaded_file):
        if image:
            if not input_text:
                input_text = "No prompt provided."
            response = get_gemini_response(input_text, image)
        else:
            response = "No image provided."

        # Display response and save to session state
        st.subheader("👇 Brief Description of the Image")
        st.write(response)

        st.session_state.imagechat_messages[unique_chat_id].append(
            {"role": 'user',
             "content": f"Prompt: {input_text}\nImage: {uploaded_file.name if uploaded_file else 'None'}"}
        )
        st.session_state.imagechat_messages[unique_chat_id].append(
            {"role": 'ai', "content": response, "avatar": AI_AVATAR_ICON}
        )

    # Generate and display response for input text
    if input_text and not submit:
        if image:
            response = get_gemini_response(input_text, image)
        else:
            response = "No image provided."

        # Display response and save to session state
        st.subheader("👇 Brief Description of the Image")
        st.write(response)

        st.session_state.imagechat_messages[unique_chat_id].append(
            {"role": 'user',
             "content": f"Prompt: {input_text}\nImage: {uploaded_file.name if uploaded_file else 'None'}"}
        )
        st.session_state.imagechat_messages[unique_chat_id].append(
            {"role": 'ai', "content": response, "avatar": AI_AVATAR_ICON}
        )
