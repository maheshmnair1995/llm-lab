from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from llm import (
    describe_image,
    answer_question,
    set_doc_context,
    set_image_context,
    extract_text_from_pdf,
    extract_text_from_docx,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

current_doc_text = None
current_image_path = None


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global current_doc_text, current_image_path
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        snippet = ""
        if file.content_type.startswith("image/"):
            current_image_path = file_path
            current_doc_text = None
            snippet = "Image uploaded."
        else:
            # PDF
            if file.filename.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            # DOCX
            elif file.filename.endswith(".docx"):
                text = extract_text_from_docx(file_path)
            # TXT
            else:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                except:
                    text = ""

            if text:
                snippet = text[:300]
                current_doc_text = text
                current_image_path = None
                set_doc_context(text)
            else:
                snippet = "Document uploaded (could not preview)."

        return {"filename": file.filename, "snippet": snippet, "message": "Upload successful"}
    except Exception as e:
        print("Error uploading file:", e)
        return {"error": "Upload failed"}


@app.post("/ask")
async def ask_question(question: str = Form(...)):
    global current_doc_text, current_image_path
    if not question.strip():
        return {"answer": "Question is empty."}

    try:
        if current_image_path:
            set_image_context(current_image_path)
            context = "image"
        elif current_doc_text:
            context = "doc"
        else:
            context = "general"

        answer = answer_question(question, context)
        return {"answer": answer}
    except Exception as e:
        print("Error in /ask:", e)
        return {"answer": "Error processing the question"}
