from qdrant_client import QdrantClient
from qdrant_client.models import (Filter, FieldCondition, MatchText)

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


def search_similar(question: str, limit: int = 3):
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

def search_keyword(term: str):
    response = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="content",
                    match=MatchText(text=term)
                )
            ]
        ),
        limit=20,
        with_payload=True
    )
    return response[0]

def search_by_filename(filename: str, limit: int = 20):
    response = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="filename",
                    match=MatchText(text=filename)
                )
            ]
        ),
        limit=limit,
        with_payload=True
    )
    return response[0]