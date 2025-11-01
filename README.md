
SBU College Chatbot Assistant

This is a Django-based chatbot assistant for Sarala Birla University (SBU). It uses a RAG (Retrieval-Augmented Generation) pipeline to answer student questions about courses, fees, admissions, and more.

It combines a local vector database (built from college documents) with a powerful large language model (LLM) to provide accurate, context-aware answers.

Features

RAG Pipeline: Searches a local ChromaDB vector store for relevant college information before answering.

LLM Integration: Uses a Mistral model via OpenRouter to generate natural, human-like answers.

Context-Aware: The bot is prompted to prefer information from the university database but can fall back on its general knowledge.

Web Interface: A clean, professional chat window (centered on the page) built with HTML, CSS, and JavaScript.

Django API: A stable backend API endpoint (/api/ask/) that handles the logic.

Tech Stack

Backend: Python, Django

AI / RAG: LangChain, OpenRouter (Mistral), ChromaDB, SentenceTransformers

Frontend: HTML, CSS, JavaScript

Environment: python-dotenv (for API keys)

Project Structure

MyCollegeChatbot/
├── .env                  # <-- STORES API KEYS (MUST CREATE)
├── .venv/                # <-- Your virtual environment
├── college_chatbot/      # Main Django project
│   ├── settings.py
│   ├── urls.py           # Main project URLs
│   └── ...
├── chat_api/             # Django app for the chatbot
│   ├── views.py          # Contains all the AI logic
│   ├── urls.py           # Defines the /api/ask/ route
│   └── ...
├── college_vector_db/    # Folder where ChromaDB stores its data
├── static/               # Frontend files
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
├── manage.py             # Django's main script
└── setup_brain.py        # (Assumed) Script to build the vector DB


Setup and Installation

Follow these steps to run the project locally.

1. Clone the Repository

git clone [https://github.com/RitikTiwari-pixle/College-chatbot-assistant.git](https://github.com/RitikTiwari-pixle/College-chatbot-assistant.git)
cd College-chatbot-assistant


2. Create and Activate Virtual Environment

# Windows
python -m venv .venv
.\.venv\Scripts\activate


3. Install Dependencies

# Install all required Python libraries
pip install django langchain langchain-openai langchain_community langchain_chroma sentence-transformers python-dotenv


(You can also save this list in a requirements.txt file and run pip install -r requirements.txt)

4. Create Your .env File

This is the most important step for fixing the 401 Error.

Create a file named .env in the root of your project (in the MyCollegeChatbot folder, next to manage.py).

Add your OpenRouter API key to it. It must be exactly like this, with no quotes:

OPENROUTER_API_KEY=sk-or-your-real-key-goes-here


5. Build the Vector Database

(This step assumes you have a script like setup_brain.py to create the database)

If your college_vector_db folder is empty, you need to run the script to build it first.

python setup_brain.py


6. Run Django Migrations

python manage.py migrate


7. Run the Server

You are now ready to start the project!

python manage.py runserver


Open your browser and go to http://127.0.0.1:8000/ to see your chatbot.
