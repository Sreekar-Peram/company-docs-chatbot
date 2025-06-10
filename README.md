# company-docs-chatbot
a chatbot that is multi-tenant in nature. The chatbot receives inputs from the user visiting their company website. When the user interacts with the website they can only ask the chatbot questions relating to the documents that the company has provided.
# Features
Upload and manage company documents via admin panel.
-  Ask questions and get answers only based on the uploaded documents (RAG-style retrieval).
-  Powered by LLaMA 3.2 running locally using Ollama.
-  Sentence/paragraph chunking and FAISS vector search for accurate retrieval.
-  Supports client-specific document separation and secure access.
-  React frontend with real-time query support.


##  Installation Guide

###  1. Clone the Repository

```bash
git clone https://github.com/Sreekar-Peram/company-docs-chatbot.git
cd company-docs-chatbot/Headrun/myproject
#Backend Setup (Django)

python -m venv venv
venv\Scripts\activate    # On Windows
# source venv/bin/activate  # On Linux/macOS

#Make sure to install FAISS and set up Ollama if not already done:
pip install faiss-cpu

Download and install Ollama: https://ollama.com

#Pull the LLaMA 3 model:
ollama pull llama3
pip install -r requirements.txt

#Frontend Setup (React)

cd myproject/frontend
npm install
npm start

# Running the Project
python manage.py runserver

#Frontend
npm start