"""
Evaluation script for the RAG Policy Q&A application.

Measures:
- Groundedness: Does the answer align with the retrieved context?
- Citation Accuracy: Does the answer cite the correct source documents?
- Latency: p50 and p95 response times
"""

import json
import os
import sys
import time
import statistics

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from app.rag.ingest import ensure_index_built
from app.rag.retriever import retrieve
from app.rag.generator import generate
from app.rag.guardrails import apply_guardrails


def load_eval_set(path):
    with open(path, "r") as f:
        return json.load(f)


def check_groundedness(answer, chunks):
    """
    Heuristic groundedness check: verify key phrases from chunks appear in the answer.
    Returns a score from 0.0 to 1.0.
    """
    if not chunks:
        return 0.0

    # Extract key phrases from chunks (sentences)
    chunk_sentences = set()
    for chunk in chunks:
        sentences = chunk["text"].replace("\n", " ").split(".")
        for sent in sentences:
            cleaned = sent.strip().lower()
            if len(cleaned) > 20:
                chunk_sentences.add(cleaned)

    if not chunk_sentences:
        return 0.5

    answer_lower = answer.lower()

    # Check how many key terms from context appear in the answer
    matches = 0
    total = 0
    for sent in chunk_sentences:
        # Extract key noun phrases (simple: 3+ word sequences)
        words = sent.split()
        for i in range(len(words) - 2):
            phrase = " ".join(words[i : i + 3])
            if len(phrase) > 10:
                total += 1
                if phrase in answer_lower:
                    matches += 1

    if total == 0:
        return 0.5

    return min(1.0, matches / max(1, total / 3))


def check_citation_accuracy(answer, citations, expected_source):
    """
    Check if the correct source document is cited.
    Returns 1.0 if expected source is in citations, 0.0 otherwise.
    """
    if not citations:
        return 0.0

    expected_lower = expected_source.lower()
    for citation in citations:
        doc = citation.get("document", "").lower()
        if expected_lower in doc or doc in expected_lower:
            return 1.0

    # Also check the answer text for source mentions
    answer_lower = answer.lower()
    if expected_lower in answer_lower:
        return 0.5

    return 0.0


def run_evaluation():
    """Run the full evaluation suite."""
    eval_dir = os.path.dirname(os.path.abspath(__file__))
    eval_set_path = os.path.join(eval_dir, "eval_set.json")
    results_path = os.path.join(eval_dir, "eval_results.json")

    # Load eval set
    eval_set = load_eval_set(eval_set_path)
    print(f"Loaded {len(eval_set)} evaluation questions\n")

    # Ensure index is built
    config = {k: getattr(Config, k) for k in dir(Config) if not k.startswith("_")}
    ensure_index_built(config)

    results = []
    latencies = []

    for item in eval_set:
        qid = item["id"]
        question = item["question"]
        expected_source = item["expected_source"]

        print(f"[{qid}/{len(eval_set)}] {question}")

        # Time the full pipeline
        start = time.time()

        # Retrieve
        chunks = retrieve(question, config)

        # Generate
        gen_result = generate(question, chunks, config)

        # Apply guardrails
        guarded = apply_guardrails(gen_result["answer"], chunks, config)

        elapsed = time.time() - start
        latencies.append(elapsed)

        # Evaluate
        groundedness = check_groundedness(guarded["answer"], chunks)
        citation_acc = check_citation_accuracy(
            guarded["answer"], guarded["citations"], expected_source
        )

        result = {
            "id": qid,
            "question": question,
            "answer": guarded["answer"],
            "expected_source": expected_source,
            "cited_sources": [c["document"] for c in guarded["citations"]],
            "groundedness_score": round(groundedness, 3),
            "citation_accuracy": round(citation_acc, 3),
            "latency_seconds": round(elapsed, 3),
            "num_chunks_retrieved": len(chunks),
            "in_scope": guarded["in_scope"],
        }
        results.append(result)

        status = "PASS" if citation_acc >= 0.5 else "MISS"
        print(f"  [{status}] Groundedness: {groundedness:.2f} | Citation: {citation_acc:.1f} | Latency: {elapsed:.2f}s\n")

    # Compute aggregate metrics
    groundedness_scores = [r["groundedness_score"] for r in results]
    citation_scores = [r["citation_accuracy"] for r in results]

    summary = {
        "total_questions": len(eval_set),
        "avg_groundedness": round(statistics.mean(groundedness_scores), 3),
        "avg_citation_accuracy": round(statistics.mean(citation_scores), 3),
        "citation_hit_rate": round(
            sum(1 for s in citation_scores if s >= 0.5) / len(citation_scores), 3
        ),
        "latency_p50": round(statistics.median(latencies), 3),
        "latency_p95": round(sorted(latencies)[int(len(latencies) * 0.95)], 3),
        "latency_avg": round(statistics.mean(latencies), 3),
    }

    output = {
        "summary": summary,
        "results": results,
    }

    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"  Total Questions:        {summary['total_questions']}")
    print(f"  Avg Groundedness:       {summary['avg_groundedness']:.3f}")
    print(f"  Avg Citation Accuracy:  {summary['avg_citation_accuracy']:.3f}")
    print(f"  Citation Hit Rate:      {summary['citation_hit_rate']:.1%}")
    print(f"  Latency p50:            {summary['latency_p50']:.3f}s")
    print(f"  Latency p95:            {summary['latency_p95']:.3f}s")
    print(f"  Latency avg:            {summary['latency_avg']:.3f}s")
    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    run_evaluation()
