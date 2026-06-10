from qdrant_client import QdrantClient

from app.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME
)

from app.embeddings import (
    generate_embedding
)

client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT
)


def search_similar(
    question: str,
    limit: int = 1
):

    vector = generate_embedding(question)

    print(f"Question: {question}")
    print(f"Embedding size: {len(vector)}")

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=limit
    )
    print(f"Results found: {len(response.points)}")
    return response.points