cat > README.md << 'EOF'
# DocMind - Document Q&A using RAG and Endee Vector Database

A production-grade RAG (Retrieval Augmented Generation) application that lets you upload documents and ask questions in plain language. Every answer is grounded in your own uploaded content.

## Live Demo
https://rag-docqa-endee-production.up.railway.app

## How It Works
1. Upload a document (text or PDF)
2. The system chunks it, embeds each chunk, and stores vectors in Endee
3. Ask a question in plain language
4. Endee performs semantic search to find the most relevant chunks
5. Groq LLM generates a grounded answer using the retrieved context

## Tech Stack
- **Vector Database:** Endee (core of the system)
- **Embeddings:** Hash-based lightweight embedder
- **LLM:** Groq (llama-3.1-8b-instant)
- **Backend:** FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Railway (Docker)

## How Endee is Used
Endee stores document chunks as 384-dimension vectors with metadata. On every question, the system embeds the query and uses Endee's similarity search to retrieve the top 5 most relevant chunks which are then passed to the LLM as context.

## Setup and Run Locally

### Prerequisites
- Docker Desktop
- Groq API key (free at console.groq.com)

### Steps
1. Clone the repository
```
git clone https://github.com/ayush-pandey047/rag-docqa-endee
cd rag-docqa-endee
```

2. Create .env file
```
cp .env.example .env
```
Add your Groq API key to .env

3. Run with Docker Compose
```
docker-compose up --build
```

4. Open http://localhost:8000

## Project Structure
```
app/
  main.py          - FastAPI routes
  chunker.py       - Text chunking
  embedder.py      - Vector embeddings
  endee_client.py  - Endee vector DB client
  rag_pipeline.py  - RAG orchestration
  gemini_client.py - LLM generation via Groq
  pdf_parser.py    - PDF text extraction
frontend/
  index.html       - UI
  style.css        - Styling
  app.js           - Frontend logic
```
EOF