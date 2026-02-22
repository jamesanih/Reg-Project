"""Generation: build prompts and call OpenRouter API for LLM responses."""

import requests


SYSTEM_PROMPT = """You are a helpful company policy assistant for Acme Corporation. Your role is to answer employee questions about company policies and procedures accurately and concisely.

Rules:
1. ONLY answer questions based on the provided context from company policy documents.
2. Always cite your sources by referencing the specific policy document and section.
3. If the context does not contain enough information to answer the question, say so clearly.
4. Keep responses under 300 words.
5. Be professional and helpful in tone.
6. Format citations as [Source: Document Name - Section] at the end of relevant statements.
7. If asked about something outside company policies, politely explain that you can only help with company policy questions."""


def build_prompt(query, chunks):
    """Construct the prompt with retrieved context chunks."""
    if not chunks:
        context = "No relevant policy documents were found for this question."
    else:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Document {i}: {chunk['source']} - {chunk['heading']}]\n{chunk['text']}"
            )
        context = "\n\n---\n\n".join(context_parts)

    user_message = f"""Based on the following company policy documents, answer the employee's question.

CONTEXT:
{context}

QUESTION: {query}

Provide a clear, accurate answer citing the specific policy documents. If the context doesn't contain relevant information, say so."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]


def generate(query, chunks, config):
    """
    Generate a response using OpenRouter API.

    Returns dict with keys: answer, citations, model
    """
    messages = build_prompt(query, chunks)

    api_key = config.get("OPENROUTER_API_KEY", "")
    model = config.get("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
    base_url = config.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
    temperature = config.get("TEMPERATURE", 0.1)

    if not api_key:
        return {
            "answer": "Error: OpenRouter API key is not configured. Please set OPENROUTER_API_KEY in your .env file.",
            "citations": [],
            "model": model,
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://acmecorp.com/policy-assistant",
        "X-Title": "Acme Policy Assistant",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 8192,
    }

    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        message = data["choices"][0]["message"]
        answer = message.get("content") or message.get("reasoning") or ""
        if not answer:
            raise KeyError("Empty response content")

        # Extract citations from the chunks used
        citations = []
        for chunk in chunks:
            citation = {
                "document": chunk["source"],
                "section": chunk["heading"],
                "relevance_score": chunk["score"],
            }
            if citation not in citations:
                citations.append(citation)

        return {
            "answer": answer,
            "citations": citations,
            "model": data.get("model", model),
        }

    except requests.exceptions.Timeout:
        return {
            "answer": "Sorry, the request timed out. Please try again.",
            "citations": [],
            "model": model,
        }
    except requests.exceptions.HTTPError:
        return {
            "answer": "Sorry, there was an error communicating with the AI service. Please try again later.",
            "citations": [],
            "model": model,
        }
    except (KeyError, IndexError):
        return {
            "answer": "Sorry, I received an unexpected response from the AI service. Please try again.",
            "citations": [],
            "model": model,
        }
    except requests.exceptions.RequestException:
        return {
            "answer": "Sorry, I couldn't connect to the AI service. Please check your internet connection and try again.",
            "citations": [],
            "model": model,
        }
