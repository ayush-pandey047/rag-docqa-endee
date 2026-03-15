# app/rag_pipeline.py

from app.embedder import embed
from app.endee_client import search
from app.gemini_client import generate_answer


def run_rag(question):
    query_vector = embed(question)
    results = search(query_vector, top_k=5)

    if not results:
        return {
            "answer": "No relevant documents found. Please upload some documents first.",
            "sources": []
        }

    context_passages = []
    sources = []

    for hit in results:
        meta   = hit.meta if hasattr(hit, "meta") else {}
        text   = meta.get("text", "")
        source = meta.get("source", "unknown")

        if text:
            context_passages.append(text)
            sources.append({"source": source, "text": text})

    answer = generate_answer(question, context_passages)

    return {
        "answer":  answer,
        "sources": sources
    }