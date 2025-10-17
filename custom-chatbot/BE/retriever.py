from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import pipeline
from .config import PERSIST_DIR, CHROMA_COLLECTION_NAME

# Embeddings
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Free RAG generative model (FLAN-T5 small)
rag_model = pipeline("text2text-generation", model="google/flan-t5-small")

def answer_query(query: str, k: int = 5) -> str:
    """
    Retrieve top-k document chunks and generate a concise answer using FLAN-T5.
    """
    chroma = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        embedding_function=embedder
    )

    retriever = chroma.as_retriever(search_kwargs={"k": k})
    docs = retriever.get_relevant_documents(query)

    if not docs:
        return "No relevant information found."

    context = " ".join([d.page_content for d in docs])

    # Use RAG to generate answer
    prompt = f"Answer the question based on the context below:\n\nContext: {context}\n\nQuestion: {query}\nAnswer:"
    result = rag_model(prompt, max_length=300, do_sample=False)[0]['generated_text']

    return result
