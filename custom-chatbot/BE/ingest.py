from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from .utils import extract_text
from .config import PERSIST_DIR, CHROMA_COLLECTION_NAME

# Initialize embeddings
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def index_documents(file_name: str, file_bytes: bytes, metadata: dict = None):
    """
    Extract text from uploaded file, split into chunks, and add to ChromaDB.
    """
    chunks = extract_text(file_name, file_bytes)
    docs_metadata = [metadata or {} for _ in chunks]

    chroma = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        embedding_function=embedder
    )

    chroma.add_texts(texts=chunks, metadatas=docs_metadata)
    chroma.persist()

    return {"ingested_chunks": len(chunks), "file": file_name}
