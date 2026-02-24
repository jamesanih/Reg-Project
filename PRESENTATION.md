# Acme Policy RAG Assistant — Presentation Script
### Quantic AI Engineering Project | 5–10 Minute Demo | 10 Slides

---

## PRESENTER SPLIT

| Presenter | Slides | Focus | Time |
|-----------|--------|-------|------|
| **Person 1** | 1–4 | Intro, requirements, corpus & architecture, design decisions | ~3 min |
| **Person 2** | 5–7 | RAG pipeline & guardrails, web app, CI/CD & deployment | ~3 min |
| **Person 3** | 8–10 | Evaluation results, AI tooling, live demo & summary | ~3.5 min |

---
---

# PERSON 1 — Overview, Architecture & Design

---

## SLIDE 1 — Title & Introduction *(Person 1)*

**What to say:**
> "Good [morning/afternoon]. I'm [Name], joined by [Name] and [Name]. We're presenting our Quantic AI Engineering Project — the Acme Policy RAG Assistant. This is a Retrieval-Augmented Generation application that lets employees ask plain-language questions about company policies and receive accurate, cited answers in seconds. I'll cover the project requirements, corpus, and architecture. [Name] will walk through the technical implementation, and [Name] will cover our evaluation results and live demo."

---

## SLIDE 2 — What the PRD Required *(Person 1)*

**What to say:**
> "The PRD had eight deliverables. The core ask was a complete RAG pipeline — ingest a corpus of policy documents, embed and index them, retrieve relevant chunks at query time, and generate grounded cited answers through a free-tier LLM. Beyond the application itself, we needed a CI/CD pipeline, documented evaluation metrics, and design documentation explaining every technology choice."

**Requirements checklist on slide:**
- Corpus: 5–20 policy documents, legally includable in the repo
- Full RAG pipeline: ingest → embed → retrieve → generate
- Web app: `/` chat UI, `/chat` API endpoint, `/health` status check
- Guardrails: scope enforcement, citation, output length
- Evaluation: groundedness + citation accuracy + latency p50/p95
- GitHub Actions CI/CD on push/PR
- Optional deployment to Railway or Render
- README, design-and-evaluation.md, ai-tooling.md

> "We met every mandatory requirement and completed the optional Railway deployment."

---

## SLIDE 3 — Corpus & System Architecture *(Person 1)*

**What to say:**
> "We assembled 12 synthetic Acme Corporation policy documents — PTO, remote work, expenses, travel, security, data privacy, code of conduct, equipment, health & safety, holidays, onboarding, and performance reviews. All authored with AI assistance using entirely synthetic data, so there are no legal or confidentiality concerns with including them in the repository. These 12 documents were parsed, chunked, and indexed into 225 vectors stored in ChromaDB."

**Architecture summary on slide:**
```
User Question
     │
     ▼
Flask Web Server  (/  /chat  /health)
     │
     ▼
Retriever  ──────▶  ChromaDB (225 chunks)
     │                    ▲
     ▼               Ingest Pipeline
Generator (OpenRouter)         │
     │               12 Markdown Policy Docs
     ▼
Guardrails (scope · citation · length)
     │
     ▼
Cited Answer
```

> "Four stages: ingestion runs once and persists to disk, retrieval and generation run on every query, guardrails validate output before it reaches the user."

---

## SLIDE 4 — Design Decisions *(Person 1)*

**What to say:**
> "Every technology choice is documented and justified in design-and-evaluation.md. Here are the four key decisions."

| Component | Choice | Why |
|-----------|--------|-----|
| **Embedding model** | BAAI/bge-small-en-v1.5 via fastembed/ONNX | Runs fully locally — no API cost, ~80MB fits Railway free-tier 512MB limit, no PyTorch dependency |
| **Vector store** | ChromaDB (local persistent) | Zero config, built-in cosine similarity, right-sized for 225 chunks, no external service needed |
| **LLM** | OpenRouter free tier | Unified OpenAI-compatible API, model swappable via one env variable, zero cost |
| **Chunking** | Heading-based + token window fallback | Policy docs have clear H1/H2/H3 structure — each chunk = one logical section; 50-token overlap prevents boundary loss |

> "I'll now hand over to [Name] who will walk through how the system runs at query time."

---
---

# PERSON 2 — Pipeline, Guardrails, Web App, CI/CD & Deployment

---

## SLIDE 5 — RAG Pipeline & Guardrails *(Person 2)*

**What to say:**
> "I'm [Name]. When a user submits a question, five steps happen in sequence. First, the query is embedded using the same BAAI model used to index the corpus — producing a 384-dimensional vector. Second, ChromaDB runs a cosine similarity search and returns the top-3 most relevant chunks above a 0.3 similarity threshold. Third, those chunks are injected into a structured prompt alongside the system instructions. Fourth, the prompt is sent to OpenRouter capped at 600 tokens. Fifth — before the answer reaches the user — three guardrails run."

**Guardrails table on slide:**

| Guardrail | Trigger | Behaviour |
|-----------|---------|-----------|
| **Scope check** | Best chunk similarity < 0.3 | Refuses: *"I can only answer about Acme Corporation's policies"* |
| **Citation enforcement** | No source reference in answer | Automatically appends a Sources section from retrieved chunks |
| **Length limit** | Answer > 300 words | Truncates at the nearest sentence boundary |

> "The scope check prevents hallucination when no relevant context was found. Out of 25 evaluation questions, it correctly refused the two questions that fell outside the indexed content."

---

## SLIDE 6 — Web Application *(Person 2)*

**What to say:**
> "The web app is built with Flask 3.0 and a vanilla HTML/CSS/JavaScript frontend — no framework dependencies, which keeps the Docker image lean. It exposes the three endpoints the PRD required."

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Chat UI — text input, response display, citation cards with source snippets and relevance scores |
| `POST` | `/chat` | Accepts JSON question → returns answer, structured citations, snippets, and latency |
| `GET` | `/health` | Returns `{"status": "ok", "service": "Acme Policy RAG Assistant"}` |

**Sample `/chat` response on slide:**
```json
{
  "answer": "The per-person limit for client entertainment is $100...",
  "citations": [
    {"document": "Expense Policy", "section": "3.1 Meals and Entertainment",
     "relevance_score": 0.85}
  ],
  "latency_seconds": 10.1
}
```

---

## SLIDE 7 — CI/CD & Deployment *(Person 2)*

**What to say:**
> "A GitHub Actions workflow runs on every push and pull request to main. It runs a matrix build across Python 3.10 and 3.11, installs all dependencies, verifies that all app imports succeed, runs the smoke test suite, and on a successful merge to main it triggers an automatic deployment to Railway via webhook."

**CI/CD pipeline on slide:**
```
Push / PR to main
       │
       ▼
GitHub Actions
  ├── Python 3.10 + 3.11 matrix
  ├── pip install -r requirements.txt
  ├── python -c "import app"      ← build check
  ├── pytest tests/ -q            ← smoke tests
  └── Railway deploy hook         ← auto-deploy on main
```

**Railway deployment:**
- Builder: Dockerfile
- Health check: `GET /health` — Railway waits for 200 before routing traffic
- Restart policy: on failure, max 3 retries
- Secrets (`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`) managed in Railway dashboard — never in the repo
- Vector index is pre-built and committed to disk — app starts immediately, no 30s re-indexing on cold start

> "I'll hand over to [Name] who will walk through our evaluation results and a live demonstration."

---
---

# PERSON 3 — Evaluation, AI Tooling & Live Demo

---

## SLIDE 8 — Evaluation Results *(Person 3)*

**What to say:**
> "I'm [Name]. We evaluated the system against 25 questions covering all 12 policy topics — a mix of factual lookup, procedural, and synthesis questions, each with a gold-standard expected source document."

**Summary scores on slide:**

| Metric | Score |
|--------|-------|
| Questions passed | **23 / 25 (92%)** |
| Avg Groundedness | **0.249 / 1.0** |
| Avg Citation Accuracy | **0.900 / 1.0** |
| Citation Hit Rate | **92%** |
| Latency p50 | **12.6s** |
| Latency p95 | **15.9s** |

**Selected results:**

| Question | Groundedness | Citation | Result |
|----------|-------------|---------|--------|
| What is the performance rating scale? | **1.00** | 1.0 | Best |
| What are the password requirements? | **1.00** | 1.0 | Best |
| Anti-harassment policy? | 0.56 | 1.0 | Strong |
| Year-end shutdown period? | 0.56 | 1.0 | Strong |
| Hybrid in-office days? | 0.03 | 0.0 | **MISS** |
| Employee records retention? | 0.00 | 0.0 | **MISS** |

---

## SLIDE 9 — Understanding the Scores & AI Tooling *(Person 3)*

**What to say:**
> "Three things worth explaining about these numbers."

**Groundedness (0.249):**
> "Our heuristic measures exact phrase overlap between the answer and source chunks. It deflates whenever the model paraphrases — which is actually good behaviour. Question 17 about flight class scored 0.06 groundedness, yet the answer 'For a 6-hour flight, you must book premium economy' is factually correct and fully sourced. Citation accuracy at 90% is the more reliable quality signal."

**The 2 misses:**
> "Question 3 — hybrid in-office days — the retriever pulled chunks from the Holiday Schedule instead of the Remote Work Policy. Hybrid search combining BM25 keyword matching with semantic search would resolve this. Question 19 — employee records retention — the answer exists in the Data Privacy Policy but wasn't within the top-3 retrieved chunks. Increasing K would surface it."

**Latency (12–16s):**
> "The current model is qwen/qwen3-vl-235b-a22b-thinking — a 235B reasoning model that runs an internal chain-of-thought. When we benchmarked google/gemma-3-4b-it, p50 dropped to ~3s. Latency is a configuration trade-off, not a structural limitation."

**AI Tooling on slide:**

| Tool | Role |
|------|------|
| **Claude Code** | Architecture design, all code, corpus authoring, evaluation scripts, CI/CD config, documentation |
| **OpenRouter LLM** | Runtime answer generation |
| **fastembed / BAAI** | Local embedding — indexing and retrieval |

---

## SLIDE 10 — Live Demo & Summary *(Person 3)*

**What to say:**
> "Let me show the application running at http://localhost:5000."

**Demo script:**

1. **Strong answer** — ask *"What is the performance rating scale?"*
   > "This scored perfect groundedness — the model lists all five levels exactly as they appear in the Performance Review Policy with the section cited."

2. **Practical answer** — ask *"What are the password requirements?"*
   > "Perfect groundedness again. The answer pulls the exact requirements from the Security Policy — 12 characters minimum, uppercase, lowercase, number, special character, 90-day rotation."

3. **Guardrail firing** — ask *"What is the weather in New York today?"*
   > "The scope guardrail fires. No chunks score above the threshold so the system refuses and directs the user to ask about company policies."

4. **Show `/health` endpoint**
   > "Simple JSON health check used by Railway for deployment monitoring."

**Summary rubric table on slide:**

| PRD Requirement | Status |
|----------------|--------|
| 12 policy documents, 225 indexed chunks | Complete |
| Full RAG pipeline | Complete |
| 3 guardrails | Complete |
| `/`, `/chat`, `/health` endpoints | Complete |
| 25-question evaluation set | Complete |
| Groundedness + Citation Accuracy metrics | 0.249 / 0.900 |
| Latency p50 / p95 | 12.6s / 15.9s |
| GitHub Actions CI/CD | Complete |
| Railway deployment | Complete |
| README + design doc + AI tooling doc | Complete |

> "Thank you for watching. The repository is shared with quantic-grader and all documentation is in place."

---

## TIMING GUIDE

| Presenter | Slides | Time |
|-----------|--------|------|
| Person 1 | 1–4 | ~3 min |
| Person 2 | 5–7 | ~3 min |
| Person 3 | 8–10 | ~3.5 min |
| **Total** | **10 slides** | **~9.5 min** |

## HANDOFF CUES

- **Person 1 → Person 2:** *"...50-token overlap prevents information loss at boundaries. I'll hand over to [Name] who'll walk through how the system runs at query time."*
- **Person 2 → Person 3:** *"...the vector index is pre-built so the app starts immediately on every deploy. Over to [Name] for our evaluation results and live demo."*
