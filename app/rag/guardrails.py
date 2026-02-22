"""Guardrails: scope checking, output filtering, and citation enforcement."""


def check_scope(chunks, threshold=0.3):
    """
    Check if retrieved chunks are relevant enough to answer the question.

    Returns (is_in_scope, message)
    """
    if not chunks:
        return False, "I can only answer questions about Acme Corporation's company policies and procedures. I couldn't find any relevant policy information for your question. Please try rephrasing or ask about a specific policy topic like PTO, remote work, expenses, security, etc."

    # Check if the best chunk score is above threshold
    best_score = max(chunk["score"] for chunk in chunks)
    if best_score < threshold:
        return False, "I can only answer questions about Acme Corporation's company policies and procedures. Your question doesn't seem to closely match any of our policy documents. Please try asking about a specific policy topic."

    return True, ""


def enforce_citations(answer, chunks):
    """
    Check if the answer references source documents.
    If not, append a sources section.
    """
    if not chunks:
        return answer

    # Check if answer already contains source references
    has_citations = any(
        indicator in answer.lower()
        for indicator in ["[source:", "source:", "according to", "policy", "per the"]
    )

    if not has_citations:
        # Append source references
        sources = set()
        for chunk in chunks:
            sources.add(f"{chunk['source']} - {chunk['heading']}")

        source_list = "\n".join(f"- {s}" for s in sorted(sources))
        answer += f"\n\n**Sources:**\n{source_list}"

    return answer


def limit_length(answer, max_words=300):
    """Truncate answer if it exceeds the word limit."""
    words = answer.split()
    if len(words) <= max_words:
        return answer

    # Truncate at word boundary and add indicator
    truncated = " ".join(words[:max_words])
    # Try to end at a sentence boundary
    last_period = truncated.rfind(".")
    if last_period > len(truncated) * 0.7:
        truncated = truncated[: last_period + 1]

    return truncated


def apply_guardrails(answer, chunks, config):
    """Apply all guardrails to the generated answer."""
    max_words = config.get("MAX_RESPONSE_WORDS", 300)
    threshold = config.get("SIMILARITY_THRESHOLD", 0.3)

    # Check scope
    in_scope, scope_message = check_scope(chunks, threshold)
    if not in_scope:
        return {
            "answer": scope_message,
            "citations": [],
            "in_scope": False,
        }

    # Enforce citations
    answer = enforce_citations(answer, chunks)

    # Limit length
    answer = limit_length(answer, max_words)

    # Build citation list
    citations = []
    seen = set()
    for chunk in chunks:
        key = (chunk["source"], chunk["heading"])
        if key not in seen:
            seen.add(key)
            citations.append({
                "document": chunk["source"],
                "section": chunk["heading"],
                "relevance_score": chunk["score"],
            })

    return {
        "answer": answer,
        "citations": citations,
        "in_scope": True,
    }
