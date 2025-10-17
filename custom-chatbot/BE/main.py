from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel

from .ingest import index_documents
from .retriever import answer_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest")
async def ingest(file: UploadFile, source_name: Optional[str] = Form(None)):
    try:
        file_bytes = await file.read()
        metadata = {"source_name": source_name or file.filename}
        res = index_documents(file.filename, file_bytes, metadata=metadata)
        return JSONResponse({"status": "ok", **res})
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

class QueryReq(BaseModel):
    query: str
    k: Optional[int] = 5

@app.post("/query")
async def query(req: QueryReq):
    try:
        answer = answer_query(req.query, k=req.k)
        return JSONResponse({"answer": answer})
    except Exception as e:
        return JSONResponse({"answer": "", "error": str(e)}, status_code=500)

@app.get("/health")
async def health():
    return {"status": "ok"}
