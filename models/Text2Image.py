def gemini_text2image():
    import streamlit as st
    from PIL import Image, UnidentifiedImageError
    import io
    import requests
    import google.generativeai as genai
    from datetime import datetime

    # Configure the API key directly using Streamlit secrets
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Get the username and unique ID from session state
    username = st.session_state.get('username', 'guest')
    user_unique_id = st.session_state.get('user_unique_id', None)
    if user_unique_id is None:
        st.session_state['user_unique_id'] = str(current_time)  # Assign a unique ID to the user if not already present

    # Initialize the history in session state
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    # Function to query the Stability Diffusion API
    def query_stabilitydiff(prompt, headers):
        API_URL = st.secrets["STABLE_DIFFUSION_API_URL"]
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        return response.content, response.status_code

    # Function to generate a prompt using Google's Generative AI
    def generate_prompt(user_input, variant):
        generation_configure = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 1000,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
        model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_configure,
            safety_settings=safety_settings
        )
        structured_prompt = f"Create an image of a {user_input} in a {variant} style. Describe lighting, mood, and color briefly."
        response = model.generate_content(structured_prompt)

        if response and response.candidates:
            output_text = response.candidates[0].content.parts[0].text if response.candidates[
                0].content.parts else "No content parts found."
            output_text = "".join([char for char in output_text if char.isprintable()])
        else:
            output_text = "No response generated."
        return output_text

    # Function to generate an image from a prompt
    def image_generation(input_prompt):
        api_key = st.secrets["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}
        image_bytes, status_code = query_stabilitydiff(input_prompt, headers)

        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Display image directly in Streamlit
            with st.chat_message("assistant"):
                st.image(image, caption=input_prompt, width=420)

            # Append history with image
            st.session_state['history'].append(
                {"role": "assistant", "content": f"Generated image based on prompt: {input_prompt}",
                 "image": image_bytes}
            )
        except (UnidentifiedImageError, IOError) as e:
            error_msg = str(e) if status_code != 200 else "Failed to generate image."
            st.session_state['history'].append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.write(error_msg)

    # Set up the Streamlit page configuration
    st.header("Generate Image From Text 🏞️", divider="rainbow")

    # Sidebar options
    if st.sidebar.button('Clear Chat History'):
        st.session_state['history'] = []

    st.sidebar.markdown("Use this option to generate descriptive prompt 👇")

    # Display existing chat history
    for message in st.session_state['history']:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "image" in message:
                st.image(Image.open(io.BytesIO(message["image"])), caption="Generated Image", use_container_width=True)

    # Get user input
    use_prompt_generation = st.sidebar.chat_input("Write key words")
    variant = st.sidebar.selectbox("Select image variant",
                                   ("Realistic", "Creative", "Minimalist", "Abstract", "Photorealistic", "Vector"))
    prompt = st.chat_input("Write your imagination")

    # Generate prompt and image if use_prompt_generation is provided
    if use_prompt_generation:
        descriptive_prompt = generate_prompt(use_prompt_generation, variant)
        st.session_state['history'].append({"role": "user", "content": descriptive_prompt})
        with st.chat_message("user"):
            st.write(f"Generated prompt: {descriptive_prompt}")
        with st.spinner('Generating image...'):
            image_generation(descriptive_prompt)

    # Directly generate image if prompt is provided
    elif prompt:
        st.session_state['history'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(f"You: {prompt}")
        with st.spinner('Generating image...'):
            image_generation(prompt)
