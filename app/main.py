# app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os

from app.chunker import chunk_text
from app.embedder import embed
from app.endee_client import create_index, upsert_vectors
from app.rag_pipeline import run_rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_index()
        print("Endee index ready.")
    except Exception as e:
        print(f"Index setup warning: {e}")
    yield


app = FastAPI(
    title="Document Q&A using RAG and Endee",
    description="Upload documents and ask questions. Powered by Endee vector database and Gemini.",
    version="1.0.0",
    lifespan=lifespan
)


class UploadRequest(BaseModel):
    text: str
    source_name: str = "document"


class QuestionRequest(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(frontend_path, "r") as f:
        return f.read()


@app.post("/upload")
def upload_document(request: UploadRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")

    chunks = chunk_text(request.text, source_name=request.source_name)

    chunks_with_vectors = []
    for chunk in chunks:
        vector = embed(chunk["text"])
        chunks_with_vectors.append({
            "id": chunk["id"],
            "vector": vector,
            "text": chunk["text"],
            "source": chunk["source"]
        })

    upsert_vectors(chunks_with_vectors)

    return {
        "message": f"Document uploaded and indexed successfully.",
        "chunks_created": len(chunks)
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = run_rag(request.question)
    return result