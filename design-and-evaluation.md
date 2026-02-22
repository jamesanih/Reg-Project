# Design & Evaluation Document

## 1. Design Decisions

### 1.1 RAG Architecture

The application follows a standard Retrieve-Augment-Generate pattern:

1. **Ingest** - Policy documents are parsed, chunked, embedded, and stored in a vector database
2. **Retrieve** - User queries are embedded and matched against stored chunks via cosine similarity
3. **Generate** - Retrieved context is injected into a prompt sent to an LLM
4. **Guardrails** - Output is validated for scope, citations, and length

This architecture was chosen for its simplicity, debuggability, and effectiveness for domain-specific Q&A tasks.

### 1.2 Embedding Model: all-MiniLM-L6-v2

**Why this model:**
- Runs locally (no API cost, no latency for embedding)
- 384-dimensional embeddings keep the vector store compact
- Strong performance on semantic similarity benchmarks for its size
- Fast inference (~14ms per sentence on CPU)
- Well-suited for the document sizes in our corpus

**Alternatives considered:**
- OpenAI `text-embedding-3-small`: Better quality but adds API cost and dependency
- `all-mpnet-base-v2`: Higher quality but 2x slower and larger

### 1.3 Vector Store: ChromaDB

**Why ChromaDB:**
- Zero configuration - runs as a local persistent store
- Built-in support for cosine similarity search
- Python-native with simple API
- Suitable for our corpus size (~100-200 chunks)

**Alternatives considered:**
- FAISS: More performant at scale but requires more setup
- Pinecone: Managed service adds cost and external dependency
- Weaviate: Overkill for our document count

### 1.4 LLM: OpenRouter Free Tier (Llama 3.1 8B)

**Why OpenRouter + Llama 3.1 8B:**
- Free tier eliminates cost concerns
- Llama 3.1 8B provides good instruction-following capability
- OpenRouter provides a unified API compatible with OpenAI format
- Easy to swap models by changing a config variable

**Alternatives considered:**
- OpenAI GPT-4o-mini: Higher quality but costs money
- Local Ollama: Requires GPU or significant CPU resources
- Mistral 7B (also free on OpenRouter): Comparable quality, Llama 3.1 chosen for broader community support

### 1.5 Chunking Strategy

**Approach: Heading-based chunking with token window fallback**

Documents are first split by markdown headings (H1/H2/H3), preserving natural section boundaries. Sections exceeding the 512-token limit are further split using sliding windows with 50-token overlap.

**Why this approach:**
- Policy documents have clear heading structure making heading-based splits semantically meaningful
- Each chunk corresponds to a logical policy section
- Token window fallback handles unusually long sections
- 50-token overlap prevents information loss at chunk boundaries

### 1.6 Guardrails

Three guardrails are applied to every response:

1. **Scope Check**: If no retrieved chunks exceed the similarity threshold (0.3), the system refuses to answer and directs the user to ask about company policies
2. **Citation Enforcement**: Ensures every answer references source documents
3. **Length Limiting**: Truncates responses exceeding 300 words at sentence boundaries

### 1.7 Web UI Design

A clean, single-page chat interface was chosen for:
- Familiar conversational UX
- Citation cards with expandable source snippets for transparency
- Responsive design for desktop and mobile
- No JavaScript framework dependencies (vanilla JS)

## 2. Evaluation Methodology

### 2.1 Evaluation Set

25 question-answer pairs covering all 12 policy documents, with:
- 2 questions per policy topic (some topics have 3)
- Mix of factual lookup, procedural, and synthesis questions
- Gold-standard expected answers and source documents

### 2.2 Metrics

#### Groundedness Score (0.0 - 1.0)
Measures whether the answer is supported by the retrieved context. Uses a heuristic approach checking if key phrases from retrieved chunks appear in the generated answer. A score of 1.0 means the answer closely tracks the source material.

#### Citation Accuracy (0.0 - 1.0)
Checks if the expected source document appears in the returned citations. A score of 1.0 means the correct document was cited, 0.5 if it was mentioned in the text but not in structured citations, 0.0 if missing entirely.

#### Citation Hit Rate
Percentage of questions where the correct source document was cited (score >= 0.5).

#### Latency
- **p50**: Median response time
- **p95**: 95th percentile response time
- Measured end-to-end (retrieval + generation + guardrails)

### 2.3 Results

Results from running `python evaluation/run_eval.py` are saved to `evaluation/eval_results.json`. Run the evaluation after setup to generate results specific to your configuration.

### 2.4 Known Limitations

1. **Groundedness metric is heuristic-based**: A more robust approach would use an LLM-as-judge, but this adds cost and latency to evaluation
2. **Free-tier LLM quality**: Llama 3.1 8B occasionally produces less polished answers compared to larger models
3. **Single-turn only**: The system doesn't maintain conversation history across questions
4. **No re-ranking**: A cross-encoder re-ranker could improve retrieval precision
5. **Synthetic corpus**: Real company policies would have more edge cases and ambiguity

## 3. Future Improvements

1. **Conversation history**: Add multi-turn context for follow-up questions
2. **Cross-encoder re-ranking**: Use a cross-encoder to re-rank retrieved chunks
3. **Hybrid search**: Combine semantic search with BM25 keyword search
4. **LLM-as-judge evaluation**: Use a capable LLM to evaluate groundedness and answer quality
5. **User feedback loop**: Collect thumbs up/down to improve retrieval over time
6. **Admin interface**: Allow policy documents to be uploaded and re-indexed through a web UI
