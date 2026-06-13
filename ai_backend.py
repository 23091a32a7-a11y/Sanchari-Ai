"""
AI Backend for Sanchari AI
Supports:
  1. Local Inference via Ollama  (privacy-first, fully offline)
  2. Cloud providers via BYOK    (Anthropic, OpenAI, Google Gemini, Groq)
"""

import json
import requests
from typing import Generator

# ── Provider configurations ───────────────────────────────────────────────────

CLOUD_PROVIDERS = {
    "Anthropic (Claude)": {
        "models": ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
        "default_model": "claude-3-5-haiku-20241022",
        "key_hint": "sk-ant-...",
        "docs": "https://console.anthropic.com/",
    },
    "OpenAI (GPT)": {
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "default_model": "gpt-4o-mini",
        "key_hint": "sk-...",
        "docs": "https://platform.openai.com/",
    },
    "Google (Gemini)": {
        "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
        "default_model": "gemini-1.5-flash",
        "key_hint": "AIza...",
        "docs": "https://aistudio.google.com/",
    },
    "Groq": {
        "models": ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"],
        "default_model": "llama-3.3-70b-versatile",
        "key_hint": "gsk_...",
        "docs": "https://console.groq.com/",
    },
}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "te": "Telugu (తెలుగు)",
    "ta": "Tamil (தமிழ்)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "mr": "Marathi (मराठी)",
}


def build_system_prompt(language_code: str = "en") -> str:
    """Build a system prompt that enforces the selected UI language."""
    lang_name = LANGUAGE_NAMES.get(language_code, "English")
    return f"""You are Sanchari AI — a knowledgeable, friendly, and culturally-aware travel assistant specialising in India.

Your expertise covers:
- Destinations across all Indian states and union territories
- Local cuisine, culture, festivals, and customs
- Transportation (trains, buses, flights, auto-rickshaws, local ferries)
- Budget planning in Indian Rupees (₹)
- Safety tips, best travel seasons, and hidden gems
- Heritage sites, national parks, temples, beaches, mountains, and backwaters

Guidelines:
- IMPORTANT: You MUST always respond ONLY in {lang_name}. This is mandatory — do not switch to any other language regardless of what language the user writes in.
- Use Indian cultural context naturally (mention chai, dhabas, IRCTC, etc.)
- Format itineraries clearly with day-by-day breakdowns.
- Include practical tips: approximate costs in ₹, local transport options, and booking advice.
- Be warm, enthusiastic, and encouraging about Indian travel.
- When suggesting food, mention regional specialties authentically.
- Mention important travel advisories or seasonal considerations when relevant.
"""


def build_messages(history: list[dict], user_message: str) -> list[dict]:
    """Convert Streamlit chat history + new message into provider-agnostic format."""
    messages = []
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_message})
    return messages


# ── Ollama (local) ─────────────────────────────────────────────────────────────

def list_ollama_models(base_url: str = "http://localhost:11434") -> list[str]:
    """Return locally available Ollama models."""
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=3)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return []


def ollama_chat(
    messages: list[dict],
    model: str,
    base_url: str = "http://localhost:11434",
    system_prompt: str = "",
) -> Generator[str, None, None]:
    """Stream a response from a local Ollama model."""
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": True,
    }
    with requests.post(
        f"{base_url}/api/chat",
        json=payload,
        stream=True,
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                chunk = json.loads(line)
                delta = chunk.get("message", {}).get("content", "")
                if delta:
                    yield delta
                if chunk.get("done"):
                    break


# ── Anthropic (Claude) ─────────────────────────────────────────────────────────

def anthropic_chat(
    messages: list[dict],
    model: str,
    api_key: str,
    system_prompt: str = "",
) -> Generator[str, None, None]:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 2048,
        "system": system_prompt,
        "messages": messages,
        "stream": True,
    }
    with requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        stream=True,
        timeout=60,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                text = line.decode("utf-8") if isinstance(line, bytes) else line
                if text.startswith("data: "):
                    data = text[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk.get("delta", {}).get("text", "")
                        if delta:
                            yield delta
                    except json.JSONDecodeError:
                        pass


# ── OpenAI ─────────────────────────────────────────────────────────────────────

def openai_chat(
    messages: list[dict],
    model: str,
    api_key: str,
    system_prompt: str = "",
) -> Generator[str, None, None]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": True,
        "max_tokens": 2048,
    }
    with requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        stream=True,
        timeout=60,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                text = line.decode("utf-8") if isinstance(line, bytes) else line
                if text.startswith("data: "):
                    data = text[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, KeyError, IndexError):
                        pass


# ── Google Gemini ──────────────────────────────────────────────────────────────

def gemini_chat(
    messages: list[dict],
    model: str,
    api_key: str,
    system_prompt: str = "",
) -> Generator[str, None, None]:
    # Convert to Gemini's contents format
    contents = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"maxOutputTokens": 2048},
    }
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
        f":streamGenerateContent?alt=sse&key={api_key}"
    )
    with requests.post(url, json=payload, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                text = line.decode("utf-8") if isinstance(line, bytes) else line
                if text.startswith("data: "):
                    data = text[6:]
                    try:
                        chunk = json.loads(data)
                        parts = (
                            chunk.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [])
                        )
                        for part in parts:
                            delta = part.get("text", "")
                            if delta:
                                yield delta
                    except (json.JSONDecodeError, IndexError):
                        pass


# ── Groq ───────────────────────────────────────────────────────────────────────

def groq_chat(
    messages: list[dict],
    model: str,
    api_key: str,
    system_prompt: str = "",
) -> Generator[str, None, None]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": True,
        "max_tokens": 2048,
    }
    with requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        stream=True,
        timeout=60,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                text = line.decode("utf-8") if isinstance(line, bytes) else line
                if text.startswith("data: "):
                    data = text[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, KeyError, IndexError):
                        pass


# ── Unified dispatch ───────────────────────────────────────────────────────────

def stream_response(
    history: list[dict],
    user_message: str,
    provider_type: str,          # "cloud" | "local"
    provider_name: str = "",     # e.g. "Anthropic (Claude)"
    model: str = "",
    api_key: str = "",
    ollama_url: str = "http://localhost:11434",
    language: str = "en",        # selected UI language code
) -> Generator[str, None, None]:
    """Single entry-point: route to the correct backend and stream tokens."""
    messages = build_messages(history, user_message)
    system_prompt = build_system_prompt(language)

    if provider_type == "local":
        yield from ollama_chat(messages, model, ollama_url, system_prompt)
    elif provider_name == "Anthropic (Claude)":
        yield from anthropic_chat(messages, model, api_key, system_prompt)
    elif provider_name == "OpenAI (GPT)":
        yield from openai_chat(messages, model, api_key, system_prompt)
    elif provider_name == "Google (Gemini)":
        yield from gemini_chat(messages, model, api_key, system_prompt)
    elif provider_name == "Groq":
        yield from groq_chat(messages, model, api_key, system_prompt)
    else:
        yield "⚠️ Unknown provider. Please check your settings."
