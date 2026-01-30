import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Load API Keys
load_dotenv()

# Configuration
DOCS_FOLDER = "docs"
DB_PATH = "data/chroma_db"

def ingest_documents():
    print(f"📂 Scanning '{DOCS_FOLDER}' for PDFs...")
    
    # 1. Load PDFs
    documents = []
    if not os.path.exists(DOCS_FOLDER):
        print(f"❌ Error: Folder '{DOCS_FOLDER}' not found.")
        return

    for file in os.listdir(DOCS_FOLDER):
        if file.endswith(".pdf"):
            file_path = os.path.join(DOCS_FOLDER, file)
            print(f"   - Loading: {file}")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

    if not documents:
        print("⚠️ No PDFs found!")
        return

    print(f"✅ Loaded {len(documents)} pages.")

    # 2. Split Text (Chunking)
    # We cut text into pieces of 1000 characters so the AI can find specific details easily.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    print(f"🧩 Split into {len(chunks)} text chunks.")

    # 3. Create Vector Store (ChromaDB)
    # This turns text into numbers and saves it locally.
    print("💾 Saving to Vector Database (this may take a moment)...")
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=DB_PATH
    )
    
    print("🎉 Success! Knowledge Base created in 'data/chroma_db'.")

if __name__ == "__main__":
    ingest_documents()