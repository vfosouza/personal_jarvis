from app.config import COLLECTION_NAME
from app.repositories.qdrant_repository import search_similar, search_keyword, client
from app.services.prompt_builder import build_prompt
from app.services.ollama_client import ask_llm
import time
from app.services.search import extract_search_term, is_reference_search


def retrieve_by_embedding(question: str) -> str:
    results = search_similar(question, limit=5)
    contexts = []
    for item in results:
        payload = item.payload or {}
        contexts.append(
            f"""
Arquivo: {payload.get("file")}
Repositório: {payload.get("repository")}
{payload.get("content")}
"""
        )
    return "\n\n".join(contexts)[:3000]

def retrieve_by_keyword(question: str):
    term = extract_search_term(question)
    matches = []
    scroll = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=10000,
        with_payload=True
    )
    for point in scroll[0]:
        payload = point.payload or {}
        content = payload.get("content", "")
        for line in content.splitlines():
            if term.lower() in line.lower():
                matches.append({
                    "file": payload.get("file"),
                    "line": line.strip()
                })
    return matches

def retrieve_context(question: str):
    if is_reference_search(question):
        context = retrieve_by_keyword(question)
    else:
        context = retrieve_by_embedding(question)
    return context

def build_reference_context(matches):
    context = []
    for item in matches:
        context.append(
            f"""
Arquivo:
{item['file']}

Código:
{item['line']}
"""
        )
    return "\n\n".join(context)

def answer_question(question: str):
    start = time.time()

    if is_reference_search(question):
        matches = retrieve_by_keyword(question)
        context = build_reference_context(matches)
    else:
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