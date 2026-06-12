from app.config import COLLECTION_NAME
from app.repositories.qdrant_repository import search_similar, search_keyword, client
from app.services.prompt_builder import build_prompt, build_reference_prompt
from app.services.ollama_client import ask_llm
import time
from app.services.search import extract_search_term, is_reference_search


def extract_context(content: str, term: str, window: int = 10):
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if term.lower() in line.lower():
            start = max(0, i - window)
            end = min(len(lines), i + window)
            return "\n".join(lines[start:end])
    return content[:1000]


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
    file_matches = {}  # Dicionário para agrupar por arquivo
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            offset=offset,
            with_payload=True
        )
        if not points:
            break
        for point in points:
            payload = point.payload or {}
            filename = payload.get("filename", "")
            content = payload.get("content", "")
            file_path = payload.get("file", "")
            if (term.lower() in filename.lower() or term.lower() in content.lower()):
                score = content.lower().count(term.lower())
                if term.lower() in filename.lower():
                    score += 10
                # Encontrar todas as ocorrências no conteúdo
                lines = content.splitlines()
                found_snippets = []
                for idx, line in enumerate(lines):
                    if term.lower() in line.lower():
                        snippet = extract_context(content, term, window=10)
                        found_snippets.append(snippet)
                        break  # Para a primeira ocorrência, extrair contexto completo
                # Se não achou nas linhas individuais mas achou no conteúdo geral
                if not found_snippets and term.lower() in content.lower():
                    snippet = extract_context(content, term, window=10)
                    found_snippets.append(snippet)
                # Agrupar por arquivo
                if found_snippets:
                    if file_path not in file_matches:
                        file_matches[file_path] = {
                            "filename": filename,
                            "score": score,
                            "snippets": []
                        }
                    file_matches[file_path]["snippets"].extend(found_snippets)
                    file_matches[file_path]["score"] = max(file_matches[file_path]["score"], score)
        if offset is None:
            break
    # Converter para lista ordenada por score
    matches = []
    for file_path, file_data in file_matches.items():
        matches.append({
            "file": file_path,
            "filename": file_data["filename"],
            "snippets": file_data["snippets"][:3],  # Máximo 3 snippets por arquivo
            "score": file_data["score"]
        })
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:10]  # Reduzir para 10 arquivos no máximo


def retrieve_context(question: str):
    if is_reference_search(question):
        context = retrieve_by_keyword(question)
    else:
        context = retrieve_by_embedding(question)
    return context


def build_reference_context(matches):
    if not matches:
        return "Nenhuma ocorrência encontrada."
    parts = []
    max_chars = 5000
    current_size = 0
    for match in matches:
        file_section = f"ARQUIVO: {match['file']}\n"
        # Adicionar todos os snippets do arquivo
        snippets_text = ""
        for i, snippet in enumerate(match["snippets"]):
            snippet_section = f"TRECHO {i + 1}:\n{snippet}\n"
            snippets_text += snippet_section
            if i < len(match["snippets"]) - 1:
                snippets_text += "\n"
        piece = file_section + snippets_text
        if current_size + len(piece) > max_chars:
            break
        parts.append(piece)
        current_size += len(piece)
    return "\n\n---\n\n".join(parts)


def answer_question(question: str):
    start = time.time()
    if is_reference_search(question):
        matches = retrieve_by_keyword(question)
        print(f"[REFERENCE MATCHES] {len(matches)}")
        context = build_reference_context(matches)
        prompt = build_reference_prompt(question, context)
    else:
        context = retrieve_by_embedding(question)
        prompt = build_prompt(question, context)
    print(f"[TIME] Retrieval: {time.time()-start:.2f}s")
    print(f"[PROMPT SIZE] {len(prompt)} chars")
    start_llm = time.time()
    response = ask_llm(prompt)
    print(f"[TIME] Ollama: {time.time()-start_llm:.2f}s")
    return response