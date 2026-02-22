# AI Tooling Document

## AI Tools Used in This Project

### 1. Claude Code (Anthropic)

**Purpose:** Primary development assistant for code generation, architecture design, and documentation.

**How it was used:**
- Designed the overall RAG application architecture
- Generated the Flask application code, RAG pipeline, and chat UI
- Created the 12 synthetic company policy documents in the corpus
- Wrote evaluation scripts and test suites
- Authored documentation (README, design document)
- Debugged and iterated on implementation details

**Impact:** Claude Code significantly accelerated development by generating well-structured, production-quality code across the full stack (Python backend, HTML/CSS/JS frontend, evaluation scripts, CI/CD configuration). The AI assistant helped maintain consistency across the codebase and ensured best practices were followed.

### 2. OpenRouter API (Meta Llama 3.1 8B Instruct)

**Purpose:** Large Language Model for generating answers to policy questions at runtime.

**How it was used:**
- Receives retrieved policy context and user questions
- Generates natural language answers with citations
- Follows system prompt instructions for scope, tone, and formatting

**Why this model:**
- Free tier on OpenRouter eliminates cost
- 8B parameter size provides good instruction-following for structured Q&A
- Low latency suitable for interactive chat

### 3. Sentence Transformers (all-MiniLM-L6-v2)

**Purpose:** Local embedding model for converting text to vectors for semantic search.

**How it was used:**
- Embeds policy document chunks during ingestion
- Embeds user queries at retrieval time
- Enables cosine similarity search in ChromaDB

**Why this model:**
- Runs locally (no API calls, no cost)
- Fast inference on CPU
- Good balance of quality and efficiency for document retrieval

### 4. ChromaDB

**Purpose:** Vector database for storing and searching document embeddings.

**How it was used:**
- Stores embedded policy chunks with metadata
- Performs approximate nearest neighbor search for retrieval
- Persists index to disk for fast startup

## AI-Assisted Development Workflow

1. **Architecture Planning**: Used Claude Code to design the system architecture, evaluate technology trade-offs, and create the implementation plan
2. **Corpus Generation**: AI-generated synthetic but realistic company policy documents covering 12 topics
3. **Code Implementation**: AI-assisted generation of all application code with human review and iteration
4. **Evaluation Design**: AI helped design evaluation metrics and create the 25-question evaluation set
5. **Documentation**: AI-generated documentation reviewed and refined for accuracy

## Ethical Considerations

- The corpus consists entirely of synthetic data; no real company policies were used
- The system includes guardrails to prevent hallucination and out-of-scope answers
- Citation enforcement ensures transparency about information sources
- The system clearly states it is an AI assistant and recommends verifying critical information with HR
