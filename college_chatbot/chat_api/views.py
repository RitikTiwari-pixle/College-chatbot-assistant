import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# --- LangChain & AI Imports ---
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# --- CONFIGURATION ---
DB_PERSIST_DIRECTORY = os.path.join(
    os.path.dirname(__file__), '..', '..', 'college_vector_db'
)
DOTENV_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', '.env'
)
load_dotenv(DOTENV_PATH)

# --- A. THE NEW "SMART" PROMPT ---
SYSTEM_PROMPT = """
You are a helpful and professional assistant for Sarala Birla University (SBU).

**SPECIAL RULE:** If the user asks "who created you", "who made you", or any similar question, you MUST answer: "I was created by Ritik Tiwari."

Your task is to answer the user's question.

Here is some context from the college website. USE THIS CONTEXT FIRST if it is relevant to the user's question.
If the context is not relevant or does not contain the answer, IGNORE THE CONTEXT and answer the question using your own general knowledge.

**IMPORTANT FORMATTING RULES:**
1.  **Always** format your answers professionally using Markdown.
2.  Use paragraphs for explanations.
3.  Use bullet points (like `* Item`) for lists (like courses, fees, or features).
4.  Use bold text (`**text**`) to highlight important information.

CONTEXT FROM COLLEGE WEBSITE:
{context}

USER'S QUESTION:
{question}

HELPFUL ANSWER:
"""
# ------------------------------------

# --- 1. Load AI Models and Database ---
llm = None
retriever = None
try:
    print("Loading AI models and Vector DB...")
    
    # Load the OpenRouter LLM
    llm = ChatOpenAI(
        model_name="mistralai/mistral-7b-instruct:free", 
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.3 # Reduced temperature for more factual answers
    )
    
    # Load FREE Local Embedding Model
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load the persisted Vector Database
    print(f"Loading DB from: {DB_PERSIST_DIRECTORY}")
    db = Chroma(
        persist_directory=DB_PERSIST_DIRECTORY,
        embedding_function=embeddings
    )
    
    # Create a "Retriever" to search the database
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3} 
    )
    print("✅ AI Models and DB Loaded.")
except Exception as e:
    print(f"❌ Error loading models: {e}")

# --- 2. View for the HTML Homepage ---
def chat_page(request):
    """Serves the main index.html chat page."""
    return render(request, 'index.html')


# --- 3. View for the Chatbot API (Now much simpler) ---
@csrf_exempt 
def ask_question_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    
    if not llm or not retriever:
        return JsonResponse({"error": "AI models are not loaded"}, status=500)

    try:
        data = json.loads(request.body)
        user_question = data.get("question")

        if not user_question:
            return JsonResponse({"error": "No question provided"}, status=400)
        
        print(f"Received question: {user_question}")

        # --- B. THE NEW LOGIC ---
        # 1. Get relevant college docs (if any)
        print("Searching internal database...")
        relevant_docs = retriever.invoke(user_question)
        
        context_text = ""
        source_url = "General Knowledge (via OpenRouter)" # Default to general
        
        if relevant_docs:
            print(f"Found {len(relevant_docs)} relevant docs.")
            # Build the context string
            context_text = "\n---\n".join([doc.page_content for doc in relevant_docs])
            # Set the source
            source_url = relevant_docs[0].metadata.get('source', 'College Website')
        else:
            print("No relevant docs found. Using general knowledge.")

        # 2. Create the final prompt
        final_prompt = SYSTEM_PROMPT.format(
            context=context_text,
            question=user_question
        )
        
        # 3. Get the answer
        final_answer = llm.invoke(final_prompt).content
        
        if context_text not in final_answer:
            if "i don't know" in final_answer.lower() or "based on the context" in final_answer.lower():
                 print("AI failed to find answer in context. Retrying with general knowledge...")
                 general_prompt = f"Answer the following question: {user_question}"
                 final_answer = llm.invoke(general_prompt).content
                 source_url = "General Knowledge (via OpenRouter)"
            elif not relevant_docs:
                 source_url = "General Knowledge (via OpenRouter)"

        
        # *** THIS IS THE FIX ***
        # I have changed "response" to "answer" to match your script.js
        return JsonResponse({
            "answer": final_answer,
            "source": source_url
        })

    except Exception as e:
        print(f"Error in ask_question_api: {e}")
        return JsonResponse({"error": str(e)}, status=500)

