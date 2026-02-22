"""Document ingestion: parsing, chunking, embedding, and indexing into ChromaDB."""

import os
import re
import hashlib
import chromadb
from fastembed import TextEmbedding

# Module-level singletons
_embedding_model = None
_chroma_client = None
_collection = None


def get_embedding_model(model_name):
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name=model_name)
    return _embedding_model


def get_collection(chroma_dir):
    global _chroma_client, _collection
    if _collection is None:
        _chroma_client = chromadb.PersistentClient(path=chroma_dir)
        _collection = _chroma_client.get_or_create_collection(
            name="policy_docs",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def parse_markdown(file_path):
    """Parse a markdown file and split it into sections based on headings."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    filename = os.path.basename(file_path).replace(".md", "").replace("-", " ").title()

    sections = []
    current_heading = filename
    current_content = []

    for line in content.split("\n"):
        heading_match = re.match(r"^(#{1,3})\s+(.+)", line)
        if heading_match:
            # Save previous section if it has content
            if current_content:
                text = "\n".join(current_content).strip()
                if text:
                    sections.append({
                        "heading": current_heading,
                        "content": text,
                        "source": filename,
                    })
            level = len(heading_match.group(1))
            current_heading = heading_match.group(2).strip()
            current_content = []
        else:
            current_content.append(line)

    # Don't forget the last section
    if current_content:
        text = "\n".join(current_content).strip()
        if text:
            sections.append({
                "heading": current_heading,
                "content": text,
                "source": filename,
            })

    return sections


def chunk_sections(sections, max_tokens=512, overlap_tokens=50):
    """Split sections into chunks. Small sections stay whole; large ones get windowed."""
    chunks = []

    for section in sections:
        words = section["content"].split()
        # Rough token estimate: 1 word ≈ 1.3 tokens
        estimated_tokens = int(len(words) * 1.3)

        if estimated_tokens <= max_tokens:
            chunks.append({
                "text": section["content"],
                "heading": section["heading"],
                "source": section["source"],
                "chunk_index": 0,
            })
        else:
            # Window-based chunking
            step = max(1, int(max_tokens / 1.3) - overlap_tokens)
            window_size = int(max_tokens / 1.3)
            idx = 0
            chunk_num = 0
            while idx < len(words):
                window = words[idx : idx + window_size]
                chunk_text = " ".join(window)
                chunks.append({
                    "text": chunk_text,
                    "heading": section["heading"],
                    "source": section["source"],
                    "chunk_index": chunk_num,
                })
                idx += step
                chunk_num += 1

    return chunks


def build_index(config):
    """Parse all markdown files in corpus, chunk, embed, and store in ChromaDB."""
    corpus_dir = config["CORPUS_DIR"]
    chroma_dir = config["CHROMA_DIR"]
    model_name = config["EMBEDDING_MODEL"]
    chunk_size = config.get("CHUNK_SIZE", 512)
    chunk_overlap = config.get("CHUNK_OVERLAP", 50)

    model = get_embedding_model(model_name)
    collection = get_collection(chroma_dir)

    # Parse all markdown files
    all_chunks = []
    for fname in sorted(os.listdir(corpus_dir)):
        if fname.endswith(".md"):
            fpath = os.path.join(corpus_dir, fname)
            sections = parse_markdown(fpath)
            chunks = chunk_sections(sections, max_tokens=chunk_size, overlap_tokens=chunk_overlap)
            all_chunks.extend(chunks)

    if not all_chunks:
        return 0

    # Create deterministic IDs based on content
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(all_chunks):
        content_hash = hashlib.md5(chunk["text"].encode()).hexdigest()[:12]
        chunk_id = f"{chunk['source']}_{content_hash}_{i}"
        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append({
            "source": chunk["source"],
            "heading": chunk["heading"],
            "chunk_index": chunk["chunk_index"],
        })

    # Embed all chunks (fastembed returns a generator of numpy arrays)
    embeddings = [e.tolist() for e in model.embed(documents)]

    # Upsert into ChromaDB (batch to avoid limits)
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        batch_end = min(i + batch_size, len(ids))
        collection.upsert(
            ids=ids[i:batch_end],
            documents=documents[i:batch_end],
            embeddings=embeddings[i:batch_end],
            metadatas=metadatas[i:batch_end],
        )

    return len(ids)


def ensure_index_built(config):
    """Build the index if it doesn't already have documents."""
    chroma_dir = config["CHROMA_DIR"]
    collection = get_collection(chroma_dir)

    if collection.count() == 0:
        print("Building vector index from corpus...")
        count = build_index(config)
        print(f"Indexed {count} chunks.")
    else:
        print(f"Vector index already exists with {collection.count()} chunks.")
