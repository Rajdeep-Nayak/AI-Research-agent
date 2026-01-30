from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Define paths
DB_PATH = "data/chroma_db"

def retrieve_tool(query: str):
    """
    Searches the local knowledge base (PDFs) for relevant information.
    """
    print(f"    📚 Querying Local Documents for: '{query}'")
    
    # 1. Connect to the Database
    embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)
    
    # 2. Search (Get top 3 most relevant chunks)
    results = vector_db.similarity_search(query, k=3)
    
    # 3. Format results as a string
    context_text = "\n\n".join([doc.page_content for doc in results])
    
    if not context_text:
        return "No relevant information found in local documents."
        
    return f"SOURCES FROM LOCAL DOCUMENTS:\n{context_text}"