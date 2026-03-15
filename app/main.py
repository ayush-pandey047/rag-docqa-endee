# app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os

from app.chunker import chunk_text
from app.embedder import embed
from app.endee_client import create_index, upsert_vectors
from app.rag_pipeline import run_rag
from app.pdf_parser import extract_text_from_pdf
from fastapi import FastAPI, HTTPException, UploadFile, File

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
    version="1.0.0",
    lifespan=lifespan
)

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


class UploadRequest(BaseModel):
    text: str
    source_name: str = "document"


class QuestionRequest(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index_file = os.path.join(frontend_path, "index.html")
    with open(index_file, "r") as f:
        return f.read()


@app.get("/style.css")
def serve_css():
    return FileResponse(os.path.join(frontend_path, "style.css"), media_type="text/css")


@app.get("/app.js")
def serve_js():
    return FileResponse(os.path.join(frontend_path, "app.js"), media_type="application/javascript")


@app.post("/upload")
def upload_document(request: UploadRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")

    chunks = chunk_text(request.text, source_name=request.source_name)

    chunks_with_vectors = []
    for chunk in chunks:
        vector = embed(chunk["text"])
        chunks_with_vectors.append({
            "id":     chunk["id"],
            "vector": vector,
            "text":   chunk["text"],
            "source": chunk["source"]
        })

    upsert_vectors(chunks_with_vectors)

    return {
        "message": "Document uploaded and indexed successfully.",
        "chunks_created": len(chunks)
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = run_rag(request.question)
    return result

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    text = extract_text_from_pdf(contents)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from this PDF.")

    source_name = file.filename.replace(".pdf", "")
    chunks = chunk_text(text, source_name=source_name)

    chunks_with_vectors = []
    for chunk in chunks:
        vector = embed(chunk["text"])
        chunks_with_vectors.append({
            "id":     chunk["id"],
            "vector": vector,
            "text":   chunk["text"],
            "source": chunk["source"]
        })

    upsert_vectors(chunks_with_vectors)

    return {
        "message": "PDF uploaded and indexed successfully.",
        "chunks_created": len(chunks)
    }