import os
import requests
from bs4 import BeautifulSoup
from lxml import etree
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# --- CONFIGURATION ---
# These are the URLs you used that worked.
URLS_TO_SCRAPE = [
    "https://sbu.ac.in/",
    "https://sbu.ac.in/about-us.html",
    "https://sbu.ac.in/FEE_STRUCTURE.html",
    "https://sbu.ac.in/FACULTIES.html",
    "https://sbu.ac.in/contact-us.html"
]

# Name of the folder where the database will be saved
DB_PERSIST_DIRECTORY = "college_vector_db"

# --- NO API KEY NEEDED ---
# We are running the models 100% free on your computer.
# ---------------------


def scrape_text_from_url(url):
    """Fetches and extracts clean text from a single webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for bad responses
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script/style/nav/footer tags
        for (tag) in soup(["script", "style", "nav", "footer", "header"]):
            (tag.decompose())
        
        # Get text, strip whitespace, and join lines
        text = (soup.get_text(separator=" ", strip=True))
        return (text)

    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return ""


def main():
    print("Starting data ingestion process...")
    
    # 1. Scrape Data
    all_texts = []
    print(f"Scraping {len(URLS_TO_SCRAPE)} URL(s)...")
    for (url) in URLS_TO_SCRAPE:
        print(f"  -> Scraping {url}")
        page_text = scrape_text_from_url(url)
        if (page_text):
            # We add the source URL as metadata
            all_texts.append({"text": page_text, "source": url})
        
    if not all_texts:
        print("No text scraped. Exiting. Check your URLs and network connection.")
        return

    print(f"Scraping complete. Found {len(all_texts)} pages.")
    
    # 2. Split Texts
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  # Size of each chunk
        chunk_overlap=200 # How much chunks overlap
    )
    
    documents = []
    for (doc) in all_texts:
        chunks = (text_splitter.split_text(doc["text"]))
        for (chunk) in chunks:
            # This creates 'Document' objects that LangChain can use
            documents.append({"page_content": chunk, "metadata": {"source": doc["source"]}})

    print(f"Created {len(documents)} text chunks.")

    # 3. Create Embeddings (The FREE, LOCAL way)
    print("Initializing FREE local embedding model (all-MiniLM-L6-v2)...")
    # This runs the embedding model 100% free on your computer
    # The first time you run this, it will download the model (a few hundred MB).
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 4. Store in Vector Database (Chroma)
    print(f"Creating and persisting vector store at '{DB_PERSIST_DIRECTORY}'...")
    
    # This creates the database in the specified folder
    db = Chroma.from_texts(
        texts=[doc["page_content"] for (doc) in documents],
        embedding=embeddings,
        metadatas=[doc["metadata"] for (doc) in documents],
        persist_directory=DB_PERSIST_DIRECTORY
    )
    
    print("✅ --- Success! --- ✅")
    print(f"Vector database has been created and saved in the '{DB_PERSIST_DIRECTORY}' folder.")
    print("You can now run your Django application.")

if __name__ == "__main__":
    main()

