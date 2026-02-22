"""Flask routes for the Policy RAG application."""

import time
from flask import Blueprint, render_template, request, jsonify, current_app
from app.rag.retriever import retrieve
from app.rag.generator import generate
from app.rag.guardrails import apply_guardrails

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Serve the chat UI."""
    return render_template("index.html")


@main_bp.route("/chat", methods=["POST"])
def chat():
    """Handle a chat question and return an answer with citations."""
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' field in request body"}), 400

    question = data["question"].strip()
    if not question:
        return jsonify({"error": "Question cannot be empty"}), 400

    if len(question) > 1000:
        return jsonify({"error": "Question too long (max 1000 characters)"}), 400

    config = current_app.config
    start_time = time.time()

    # Step 1: Retrieve relevant chunks
    chunks = retrieve(question, config)

    # Step 2: Check scope via guardrails
    from app.rag.guardrails import check_scope
    in_scope, scope_message = check_scope(chunks, config.get("SIMILARITY_THRESHOLD", 0.3))

    if not in_scope:
        elapsed = round(time.time() - start_time, 3)
        return jsonify({
            "answer": scope_message,
            "citations": [],
            "snippets": [],
            "latency_seconds": elapsed,
        })

    # Step 3: Generate answer
    result = generate(question, chunks, config)

    # Step 4: Apply guardrails to the answer
    guarded = apply_guardrails(result["answer"], chunks, config)

    elapsed = round(time.time() - start_time, 3)

    # Build snippets for the UI
    snippets = []
    for chunk in chunks[:5]:
        snippets.append({
            "source": chunk["source"],
            "section": chunk["heading"],
            "text": chunk["text"][:300] + ("..." if len(chunk["text"]) > 300 else ""),
            "score": chunk["score"],
        })

    return jsonify({
        "answer": guarded["answer"],
        "citations": guarded["citations"],
        "snippets": snippets,
        "latency_seconds": elapsed,
    })


@main_bp.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "service": "Acme Policy RAG Assistant",
    })
