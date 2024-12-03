# VyomAI - Your One-Stop AI Solution  

VyomAI is an advanced AI tool designed to address diverse AI needs, offering powerful and versatile functionalities across multiple domains. With VyomAI, users can interact, create, and analyze seamlessly through its comprehensive suite of five core modules.

---

## Features  

### 1. **ChatBot**  
An intelligent conversational assistant designed to provide accurate and contextual responses. Perfect for customer service, personal assistance, and real-time support.  

### 2. **Chat using Image**  
Empowers users to upload an image and receive meaningful insights, context, or responses based on the image content. Ideal for visual recognition and discussion.  

### 3. **Chat with PDF**  
Upload PDFs and interact with the document content. VyomAI can answer questions, summarize, and extract relevant information from uploaded files.  

### 4. **Text-to-Image Generation**  
Generate high-quality images from textual prompts using state-of-the-art AI models. This module is perfect for content creation, concept visualization, and more.  

### 5. **Text-to-Audio Generation**  
Convert text to realistic audio in various tones and styles, suitable for narration, accessibility features, and content creation.  

---

## How to Use  

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/username/vyomai.git  
   cd vyomai
   ``` 
2. **Install Dependencies**
Use Conda or Pip to install the required packages:
```bash
  conda create -n vyomai_env python=3.10.15  
  conda activate vyomai_env  
  pip install -r requirements.txt
```
3. **Run VyomAI**
Launch the application:
```bash
  python app.py  
```
4. Access
Open a browser and go to http://localhost:5000.

## Technologies Used
ChatBot: LLM (e.g., Llama 3.1)
Chat using Image: Image analysis via YOLO models
Chat with PDF: PDF parsing libraries (e.g., PyPDF2)
Text-to-Image: Stable Diffusion API
Text-to-Audio: Advanced text-to-speech frameworks
## Folder Structure
VyomAI/  
│  
├── modules/  
│   ├── chatbot/  
│   ├── image_chat/  
│   ├── pdf_chat/  
│   ├── text_to_image/  
│   ├── text_to_audio/  
│  
├── static/  
├── templates/  
├── app.py  
├── requirements.txt  
└── README.md  

## Contributing
We welcome contributions! To contribute:

Fork the repository.
Create a new branch (feature-branch).
Commit your changes and create a pull request.

## License
VyomAI is released under the MIT License.


  
