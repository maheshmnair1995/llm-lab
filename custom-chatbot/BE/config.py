import os

PERSIST_DIR = "chroma_db"
CHROMA_COLLECTION_NAME = "custom_chatbot"

# Ensure persist directory exists
os.makedirs(PERSIST_DIR, exist_ok=True)

# Chunk size for splitting text (in characters)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
