from app.repositories.qdrant_repository import search_similar
from app.services.prompt_builder import build_prompt
from app.services.ollama_client import ask_llm
import time


def retrieve_context(question: str) -> str:
    results = search_similar(question, limit=1)
    contexts = []
    for item in results:
        payload = item.payload or {}
        content = payload.get("content", "")
        if content:
            contexts.append(content)
    context = "\n\n".join(contexts)
    print(f"Context size: {len(context)}")
    return context[:800]

def answer_question(question: str):
    start = time.time()
    context = retrieve_context(question)
    print(f"[TIME] Retrieval: {time.time()-start:.2f}s")
    start_prompt = time.time()
    prompt = build_prompt(question, context)
    print(f"[TIME] Prompt Build: {time.time()-start_prompt:.2f}s")
    print(f"[PROMPT SIZE] {len(prompt)} chars")
    start_llm = time.time()
    response = ask_llm(prompt)
    print(f"[TIME] Ollama: {time.time()-start_llm:.2f}s")
    return response