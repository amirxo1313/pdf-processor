"""
GapGPT API Integration Models
Handles communication with multiple AI models through GapGPT API
"""
import os
import httpx
from typing import List, Dict, Any


BASE_URL = os.getenv("BASE_URL", "https://api.gapgpt.app/v1")


def query_model(model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Query a specific AI model via GapGPT API

    Args:
        model: Model name (gpt-4o, gpt-5, claude-opus-4, gemini-2.5-pro)
        messages: List of message dicts with 'role' and 'content'

    Returns:
        Response dict from the API
    """
    base_urls = {
        "gpt-4o": f"{BASE_URL}/chat/completions",
        "gpt-5": f"{BASE_URL}/chat/completions",
        "claude-opus-4": "https://api.anthropic.com/v1/messages",
        "gemini-2.5-pro": "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
    }

    apikeys = {
        "gpt-4o": os.getenv("OPENAI_API_KEY"),
        "gpt-5": os.getenv("OPENAI_API_KEY"),
        "claude-opus-4": os.getenv("CLAUDE_API_KEY"),
        "gemini-2.5-pro": os.getenv("GEMINI_API_KEY"),
    }

    if "gemini" in model:
        payload = {
            "contents": [{"role": "user", "parts": [{"text": messages[-1]['content']}]}]
        }
        headers = {"Authorization": f"Bearer {apikeys[model]}"}
    elif "claude" in model:
        payload = {"model": model, "messages": messages, "max_tokens": 1024}
        headers = {"x-api-key": apikeys[model], "Content-Type": "application/json"}
    else:
        payload = {"model": model, "messages": messages}
        headers = {
            "Authorization": f"Bearer {apikeys[model]}",
            "Content-Type": "application/json"
        }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(base_urls[model], headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": str(e), "model": model}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "model": model}


