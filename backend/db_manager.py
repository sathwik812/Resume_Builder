import os
import asyncio
import shutil
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings 
from langchain_core.documents import Document
from backend.config import settings
from pydantic import SecretStr

def _ensure_event_loop():
    """
    Ensure event loop exists for async operations.
    Required for ChromaDB and some embedding operations.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No event loop in current thread, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

def _get_chroma_persist_directory() -> str:
    """
    Get Chroma persist directory from settings with fallback options.
    """
    return getattr(
        settings,
        "CHROMA_PERSIST_DIRECTORY",
        getattr(
            settings,
            "chroma_persist_directory",
            os.path.join(os.getcwd(), "chroma_db")
        ),
    )

def get_embeddings() -> Optional[GoogleGenerativeAIEmbeddings]:
    """
    Get Google Gemini embeddings instance.
    
    Returns:
        GoogleGenerativeAIEmbeddings: Configured embeddings model or None if API key is missing
    """
    try:
        # Get API key from settings or environment
        api_key = getattr(settings, "GOOGLE_API_KEY", None) or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("Warning: GOOGLE_API_KEY not found in settings or environment variables")
            return None
        
        # Get model name from settings
        # For Google Gemini embeddings, common models are:
        # - "models/embedding-001" (default)
        # - "models/text-embedding-004" (newer)
        model_name = getattr(settings, "EMBEDDING_MODEL_NAME", "models/embedding-001")
        
        # Create Google Gemini embeddings instance
        embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            api_key=SecretStr(api_key)
            # Optional: task_type for different embedding tasks
            # task_type="retrieval_document",  # or "retrieval_query", "classification", "clustering"
        )
        
        return embeddings
        
    except ImportError:
        print("Google Gemini embeddings not available. Install with: pip install langchain-google-genai")
        return None
    except Exception as e:
        print(f"Error creating Gemini embeddings: {str(e)}")
        return None

def create_vectorstore_from_text(text: str) -> Optional[Chroma]:
    """
    Create vector store from text content using Google Gemini embeddings.
    
    Args:
        text: Input text to be chunked and embedded
        
    Returns:
        Chroma vector store or None if creation fails
    """
    _ensure_event_loop()
    
    if not text or not text.strip():
        print("Warning: Empty text provided")
        return None
    
    try:
        # Get embeddings instance
        embeddings = get_embeddings()
        if embeddings is None:
            print("Error: Could not create embeddings instance. Check GOOGLE_API_KEY configuration.")
            return None
        
        # Use getattr to avoid unknown attribute errors on settings
        chunk_size = getattr(settings, "CHUNK_SIZE", 1000)
        chunk_overlap = getattr(settings, "CHUNK_OVERLAP", 200)

        # Split text into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        chunks = splitter.split_text(text)
        
        if not chunks:
            print("Warning: No chunks created from text")
            return None
        
        print(f"Created {len(chunks)} chunks from text")
        
        # Create vector store with embeddings
        persist_dir = _get_chroma_persist_directory()
        vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        
        print(f"Vector store created successfully in {persist_dir}")
        return vector_store
        
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def get_vectorstore() -> Optional[Chroma]:
    """
    Load existing vector store from disk.
    
    Returns:
        Chroma vector store or None if not found or loading fails
    """
    _ensure_event_loop()
    
    persist_dir = _get_chroma_persist_directory()
    if not os.path.exists(persist_dir):
        print(f"Vector store directory not found: {persist_dir}")
        return None
    
    try:
        embeddings = get_embeddings()
        if embeddings is None:
            print("Error: Could not create embeddings instance for loading vector store")
            return None
            
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
        print("Vector store loaded successfully")
        return vectorstore
        
    except Exception as e:
        print(f"Error loading vector store: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def query_vectorstore(query: str, k: int = 3) -> List[Document]:
    """
    Query vector store for relevant documents using Google Gemini embeddings.
    
    Args:
        query: Search query
        k: Number of results to return
        
    Returns:
        List of relevant documents
    """
    vectorstore = get_vectorstore()
    
    if vectorstore is None:
        print("No vector store available for querying")
        return []
    
    try:
        results = vectorstore.similarity_search(query, k=k)
        print(f"Found {len(results)} relevant documents")
        return results
        
    except Exception as e:
        print(f"Error querying vector store: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def clear_vectorstore() -> bool:
    """
    Clear the vector store by deleting the persist directory.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        persist_dir = _get_chroma_persist_directory()
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            print(f"Vector store cleared: {persist_dir}")
            return True
        return False
    except Exception as e:
        print(f"Error clearing vector store: {str(e)}")
        return False