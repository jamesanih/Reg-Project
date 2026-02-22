# Acme Policy RAG Assistant

A Retrieval-Augmented Generation (RAG) application that answers employee questions about company policies and procedures. Built with Flask, ChromaDB, and OpenRouter.

## Architecture

```
User Question
     │
     ▼
┌─────────────┐
│  Flask Web   │  ← Chat UI (HTML/CSS/JS)
│   Server     │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────────┐
│  Retriever   │────▶│    ChromaDB       │
│  (Top-K)     │     │  (Vector Store)   │
└──────┬──────┘     └──────────────────┘
       │                     ▲
       │              ┌──────┴──────┐
       │              │   Ingest    │
       │              │  Pipeline   │
       │              └──────┬──────┘
       │                     │
       ▼              ┌──────┴──────┐
┌─────────────┐       │   Corpus    │
│  Generator   │       │ (12 Policy  │
│ (OpenRouter) │       │  Markdown)  │
└──────┬──────┘       └─────────────┘
       │
       ▼
┌─────────────┐
│ Guardrails   │
│ (Scope,Cite) │
└──────┬──────┘
       │
       ▼
   Response with
   Citations
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | Flask 3.0 |
| LLM | OpenRouter (Llama 3.1 8B free tier) |
| Embeddings | BAAI/bge-small-en-v1.5 via fastembed (ONNX, local) |
| Vector Store | ChromaDB (local, persistent) |
| Frontend | Custom HTML/CSS/JS chat UI |

## Quick Start

### 1. Clone and set up environment

```bash
git clone <repo-url>
cd policy-rag-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

Get a free API key at [https://openrouter.ai/keys](https://openrouter.ai/keys).

### 3. Run the application

```bash
python run.py
```

The app will:
1. Build the vector index from the corpus (first run only, takes ~30 seconds)
2. Start the Flask server on `http://localhost:5000`

### 4. Use the chat interface

Open `http://localhost:5000` in your browser and ask questions about company policies.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Chat UI |
| POST | `/chat` | Submit a question, get an answer with citations |
| GET | `/health` | Health check |

### POST /chat

**Request:**
```json
{
  "question": "How many PTO days do new employees get?"
}
```

**Response:**
```json
{
  "answer": "New full-time employees receive 15 PTO days per year...",
  "citations": [
    {"document": "Pto Policy", "section": "PTO Accrual Rates", "relevance_score": 0.85}
  ],
  "snippets": [
    {"source": "Pto Policy", "section": "PTO Accrual Rates", "text": "...", "score": 0.85}
  ],
  "latency_seconds": 2.5
}
```

## Project Structure

```
policy-rag-app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # API routes
│   ├── rag/
│   │   ├── ingest.py        # Document parsing, chunking, embedding
│   │   ├── retriever.py     # Vector similarity search
│   │   ├── generator.py     # LLM prompt + OpenRouter API
│   │   └── guardrails.py    # Scope check, citation enforcement
│   ├── templates/
│   │   └── index.html       # Chat UI
│   └── static/
│       ├── style.css
│       └── app.js
├── corpus/                   # 12 synthetic company policy documents
├── evaluation/
│   ├── eval_set.json         # 25 Q&A evaluation pairs
│   ├── run_eval.py           # Evaluation script
│   └── eval_results.json     # Results output
├── tests/
│   └── test_app.py           # Smoke tests
├── .github/workflows/ci.yml  # CI/CD pipeline
├── config.py                 # Configuration
├── run.py                    # Entry point
├── requirements.txt
├── design-and-evaluation.md
└── ai-tooling.md
```

## Running Evaluation

```bash
python evaluation/run_eval.py
```

This runs 25 questions through the full RAG pipeline and measures groundedness, citation accuracy, and latency. Results are saved to `evaluation/eval_results.json`.

## Running Tests

```bash
pytest tests/ -q
```

## Configuration

Key settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENROUTER_MODEL` | `google/gemma-3-12b-it:free` | LLM model |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Embedding model (fastembed/ONNX) |
| `CHUNK_SIZE` | 512 tokens | Max chunk size |
| `TOP_K` | 5 | Number of chunks to retrieve |
| `SIMILARITY_THRESHOLD` | 0.3 | Minimum relevance score |
| `MAX_RESPONSE_WORDS` | 300 | Max answer length |
