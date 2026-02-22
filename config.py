import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv(
        "OPENROUTER_MODEL", "deepseek/deepseek-r1-0528:free"
    )
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    # Embedding model
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

    # Chunking
    CHUNK_SIZE = 512  # tokens
    CHUNK_OVERLAP = 50  # tokens

    # Retrieval
    TOP_K = 5
    SIMILARITY_THRESHOLD = 0.3  # minimum relevance score

    # Generation
    MAX_RESPONSE_WORDS = 300
    TEMPERATURE = 0.1

    # Paths
    CORPUS_DIR = os.path.join(os.path.dirname(__file__), "corpus")
    CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
