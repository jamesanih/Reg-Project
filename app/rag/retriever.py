"""Retrieval: vector search against ChromaDB to find relevant policy chunks."""

from app.rag.ingest import get_embedding_model, get_collection


def retrieve(query, config):
    """
    Retrieve top-k relevant chunks for a given query.

    Returns a list of dicts with keys: text, source, heading, score
    """
    model = get_embedding_model(config["EMBEDDING_MODEL"])
    collection = get_collection(config["CHROMA_DIR"])

    top_k = config.get("TOP_K", 5)
    threshold = config.get("SIMILARITY_THRESHOLD", 0.3)

    # Embed the query
    query_embedding = model.encode([query]).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    chunks = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # ChromaDB cosine distance: 0 = identical, 2 = opposite
        # Convert to similarity: 1 - (distance / 2)
        similarity = 1 - (distance / 2)

        if similarity >= threshold:
            chunks.append({
                "text": doc,
                "source": meta["source"],
                "heading": meta["heading"],
                "score": round(similarity, 4),
            })

    # Sort by score descending
    chunks.sort(key=lambda x: x["score"], reverse=True)

    return chunks
