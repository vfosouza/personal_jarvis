from chunking import chunk_text
from embeddings import generate_embedding
from file_loader import load_files
from qdrant_store import create_collection_if_not_exists, save_chunk
from config import CHUNK_SIZE, CHUNK_OVERLAP

ROOT_PATH = "/repositories"

def run():
    create_collection_if_not_exists()
    point_id = 1

    for file, content in load_files(ROOT_PATH):
        print(f"Processing: {file}")

        chunks = list(chunk_text(
                        content,
                        chunk_size=CHUNK_SIZE,
                        chunk_overlap=CHUNK_OVERLAP
                    )
        )
        print(f"Chunks: {len(chunks)}")

        for chunk in chunks:
            vector = generate_embedding(chunk)

            print(
                f"Chunk len={len(chunk)} "
                f"Embedding len={len(vector)}"
            )
            save_chunk(
                point_id=point_id,
                vector=vector,
                payload={
                    "file": str(file),
                    "filename": file.name,
                    "extension": file.suffix,
                    "repository": file.parts[2],
                    "content": chunk
                }
            )

            point_id += 1

if __name__ == "__main__":
    run()
    print("Indexação concluída.")