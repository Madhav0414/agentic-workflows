import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not set in .env")

EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIM = 768
INDEX_NAME = "multimodal-rag"
METRIC = "cosine"
CHAT_MODEL = "claude-sonnet-4-20250514"

_genai_client = None

def get_genai_client():
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(api_key=GEMINI_API_KEY)
    return _genai_client
