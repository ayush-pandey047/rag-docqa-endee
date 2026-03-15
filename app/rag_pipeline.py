# app/rag_pipeline.py

from app.embedder import embed
from app.endee_client import search
from app.gemini_client import generate_answer


def run_rag(question):
    try:
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
            if isinstance(hit, dict):
                meta = hit.get("meta", {})
            else:
                meta = getattr(hit, "meta", {}) or {}

            text   = meta.get("text", "") if isinstance(meta, dict) else ""
            source = meta.get("source", "unknown") if isinstance(meta, dict) else "unknown"

            if text and len(text) > 20 and text.isascii():
                context_passages.append(text)
                sources.append({"source": source, "text": text})

        if not context_passages:
            return {
                "answer": "No readable content found. Please upload a plain text document.",
                "sources": []
            }

        answer = generate_answer(question, context_passages)

        return {
            "answer":  answer,
            "sources": sources
        }

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return {
                "answer": "API rate limit reached. Please wait 60 seconds and try again.",
                "sources": []
            }
        return {
            "answer": f"An error occurred: {error_msg}",
            "sources": []
        }