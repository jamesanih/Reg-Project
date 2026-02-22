"""Smoke tests for the Policy RAG application."""

import json
import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """Create application for testing."""
    from app import create_app
    from config import Config

    class TestConfig(Config):
        TESTING = True

    app = create_app(TestConfig)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_health_endpoint(client):
    """Test the health check endpoint returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "version" in data


def test_index_page(client):
    """Test that the index page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Acme Policy Assistant" in response.data


def test_chat_missing_question(client):
    """Test that /chat returns error when question is missing."""
    response = client.post(
        "/chat",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_chat_empty_question(client):
    """Test that /chat returns error for empty question."""
    response = client.post(
        "/chat",
        data=json.dumps({"question": "   "}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_chat_question_too_long(client):
    """Test that /chat rejects overly long questions."""
    response = client.post(
        "/chat",
        data=json.dumps({"question": "x" * 1001}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_chat_valid_question(client):
    """Test that a valid question returns a response with expected fields."""
    response = client.post(
        "/chat",
        data=json.dumps({"question": "How many PTO days do new employees get?"}),
        content_type="application/json",
    )
    # May succeed or fail depending on API key, but should return 200
    # even without API key (guardrails or error message)
    assert response.status_code == 200
    data = response.get_json()
    assert "answer" in data
    assert "citations" in data
    assert "latency_seconds" in data


def test_corpus_files_exist():
    """Verify all expected corpus files exist."""
    corpus_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus"
    )
    expected_files = [
        "pto-policy.md",
        "remote-work-policy.md",
        "expense-policy.md",
        "security-policy.md",
        "code-of-conduct.md",
        "onboarding-policy.md",
        "performance-review-policy.md",
        "holiday-schedule.md",
        "travel-policy.md",
        "data-privacy-policy.md",
        "health-safety-policy.md",
        "equipment-policy.md",
    ]
    for fname in expected_files:
        assert os.path.exists(os.path.join(corpus_dir, fname)), f"Missing: {fname}"


def test_ingest_module():
    """Test that the ingest module can parse and chunk markdown files."""
    from app.rag.ingest import parse_markdown, chunk_sections

    corpus_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus"
    )
    pto_path = os.path.join(corpus_dir, "pto-policy.md")

    sections = parse_markdown(pto_path)
    assert len(sections) > 0
    assert sections[0]["source"] == "Pto Policy"

    chunks = chunk_sections(sections)
    assert len(chunks) > 0
    assert "text" in chunks[0]
    assert "heading" in chunks[0]


def test_guardrails_scope_check():
    """Test guardrails scope check with empty chunks."""
    from app.rag.guardrails import check_scope

    in_scope, msg = check_scope([])
    assert not in_scope
    assert "company policies" in msg.lower()

    in_scope, msg = check_scope([{"score": 0.1}], threshold=0.3)
    assert not in_scope


def test_guardrails_length_limit():
    """Test guardrails length limiting."""
    from app.rag.guardrails import limit_length

    short = "This is a short answer."
    assert limit_length(short, 300) == short

    long_text = " ".join(["word"] * 500)
    result = limit_length(long_text, 300)
    assert len(result.split()) <= 301  # Allow for boundary
