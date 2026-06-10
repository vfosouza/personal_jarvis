from app.repositories.qdrant_repository import search_similar
from app.services.prompt_builder import build_prompt
from app.services.ollama_client import ask_llm


def retrieve_context(question: str) -> str:
    results = search_similar(
        question,
        limit=3)

    print(f"Results found: {len(results)}")
    contexts = []

    for item in results:
        payload = item.payload or {}
        print(
            f"Score={item.score} "
            f"File={payload.get('file')}"
        )

        content = payload.get("content", "")
        if content:
            contexts.append(content)
    context = "\n\n".join(contexts)
    return context[:1500]


def answer_question(question: str):
    context = retrieve_context(question)
    prompt = build_prompt(
        question=question,
        context=context
    )

    return ask_llm(prompt)