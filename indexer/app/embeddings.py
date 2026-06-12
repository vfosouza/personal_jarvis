from typing import List
from sentence_transformers import SentenceTransformer
from config import BATCH_SIZE

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

def generate_embedding(text: str) -> List[float]:
    """
    Gera o embedding para um único texto.
    """
    return model.encode(text).tolist()

def generate_embeddings_in_batches(texts: List[str]) -> List[List[float]]:
    """
    Processa uma lista de textos (chunks) em lotes para gerar embeddings de forma mais eficiente.
    """
    embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        batch_embeddings = model.encode(
            batch,
            batch_size=BATCH_SIZE,
            show_progress_bar=True
        )
        embeddings.extend(batch_embeddings.tolist())
    return embeddings