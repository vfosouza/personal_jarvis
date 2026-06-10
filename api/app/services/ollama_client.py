import requests
from app.config import (
    OLLAMA_MODEL,
    OLLAMA_URL
)

def ask_llm(
        prompt: str
):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=300
    )
    response.raise_for_status()
    return response.json()["response"]

def health():
    return ask_llm("Responda apenas OK")