import streamlit as st
import os
import asyncio
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

def gemini_pdf_chat():
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def get_or_create_eventloop():
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

    # Initialize the event loop
    loop = get_or_create_eventloop()

    def get_pdf_text(pdf_docs):
        text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def get_text_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        return chunks

    def get_vector_store(text_chunks, unique_id):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        st.session_state[f"{unique_id}_vector_store"] = vector_store  # Store vector store in session state

    def get_conversational_chain():
        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details, don't provide the wrong answer\n\n
        Context:\n {context}?\n
        Question: \n{question}\n

        Answer:
        """

        model = ChatGoogleGenerativeAI(model="gemini-1.0-pro", temperature=0.3)
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

        return chain

    def user_input(user_question, unique_id):
        # Ensure that the vector store exists in session state
        vector_store_key = f"{unique_id}_vector_store"
        if vector_store_key not in st.session_state:
            st.warning("Please upload and process PDF files first.")
            return None

        # Use vector store directly from session state
        vector_store = st.session_state[vector_store_key]
        docs = vector_store.similarity_search(user_question)

        chain = get_conversational_chain()
        response = chain.invoke({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        return response

    st.header("Chat with PDFs 📚", divider="rainbow")

    # Ensure a unique session identifier for each user and document
    username = st.session_state.get('username', 'guest')
    pdf_docs = st.sidebar.file_uploader("Upload your PDF Files and Click on the Submit & Process Button",
                                        accept_multiple_files=True)

    if pdf_docs:
        document_name = pdf_docs[0].name.split('.')[0]  # Use the first PDF name (without extension) as the document name
        unique_id = f"{username}_{document_name}"

        # Initialize chat history in session state if not present
        chat_history_key = f"{unique_id}_chat_history"
        if chat_history_key not in st.session_state:
            st.session_state[chat_history_key] = []

        # Display previous chat history if exists
        for message in st.session_state[chat_history_key]:
            if message["sender"] == "user":
                st.chat_message(message["sender"], avatar="👨‍💻").text(message["content"])
            else:
                st.chat_message(message["sender"], avatar="🤖").text(message["content"])

        # User input for questions
        user_question = st.chat_input("Ask a Question from the PDF Files")
        if user_question:
            st.chat_message("user", avatar="👨‍💻").text(user_question)
            st.session_state[chat_history_key].append({"sender": "user", "content": user_question})

            # Get the response
            response = user_input(user_question, unique_id)
            if response:
                response_text = response["output_text"]
                st.chat_message("assistant", avatar="🤖").text(response_text)
                st.session_state[chat_history_key].append({"sender": "assistant", "content": response_text})

    with st.sidebar:
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks, unique_id)
                st.success("Processing complete")
