import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Database and file paths
    DATA_UPLOAD_FOLDER = "data/uploads"
    VECTOR_DB_PATH = "data/vector_db"
    
    # LLM settings
    OPENAI_MODEL = "gpt-4"  # or "gpt-3.5-turbo"
    GEMINI_MODEL = "gemini-pro"
    
    # ChromaDB settings
    CHROMA_COLLECTION_NAME = "text2chart_collection"
    
config = Config()