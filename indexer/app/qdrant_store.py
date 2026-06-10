from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, VectorParams, PointStruct)
from config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME

client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT
)

def create_collection_if_not_exists():
    collections = client.get_collections()
    exists = any(
        c.name == COLLECTION_NAME
        for c in collections.collections
    )

    if exists:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

def create_collection():
    collections = client.get_collections()
    exists = any(
        c.name == "repositories"
        for c in collections.collections
    )

    if exists:
        return

    client.create_collection(
        collection_name="repositories",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

def save_chunk(
    point_id: int,
    vector: list,
    payload: dict):
    print(f"[UPSERT] id={point_id} " f"vector_size={len(vector)}")

    result = client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
        ]
    )

    print(result)