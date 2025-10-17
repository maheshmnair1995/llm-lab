import os
import docx
import PyPDF2
from io import BytesIO
from .config import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text(file_name: str, file_bytes: bytes) -> list[str]:
    """
    Extract text content from different file types (txt, pdf, docx) from in-memory bytes.
    Returns a list of strings (chunks).
    """
    ext = os.path.splitext(file_name)[-1].lower()
    full_text = ""

    if ext == ".txt":
        full_text = file_bytes.decode("utf-8")

    elif ext == ".pdf":
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            full_text += (page.extract_text() or "") + "\n"

    elif ext == ".docx":
        doc = docx.Document(BytesIO(file_bytes))
        for para in doc.paragraphs:
            full_text += para.text + "\n"

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Split into chunks
    chunks = []
    start = 0
    while start < len(full_text):
        end = min(start + CHUNK_SIZE, len(full_text))
        chunks.append(full_text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return [c.strip() for c in chunks if c.strip()]
