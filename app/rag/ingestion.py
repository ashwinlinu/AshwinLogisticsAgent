from langchain_core.documents import Document
from qdrant_client.models import PointStruct
from uuid import NAMESPACE_URL, uuid5

from app.rag.embeddings import embed_documents
from app.rag.vector_store import upsert_chunks


def ingest_chunks(chunks: list[Document]) -> int:
    if not chunks:
        return 0

    texts = [
        chunk.page_content
        for chunk in chunks
    ]

    vectors = embed_documents(texts)

    points = []

    document_chunk_counters: dict[str, int] = {}

    for chunk, vector in zip(chunks, vectors):
        document_id = chunk.metadata["document_id"]

        chunk_index = document_chunk_counters.get(
            document_id,
            0,
        )

        document_chunk_counters[document_id] = (
            chunk_index + 1
        )

        point_id = str(
            uuid5(
                NAMESPACE_URL,
                f"ashwin-logistics:{document_id}:{chunk_index}",
            )
        )

        payload = {
            "document_id": document_id,
            "title": chunk.metadata["title"],
            "category": chunk.metadata["category"],
            "version": chunk.metadata["version"],
            "source": chunk.metadata["source"],
            "effective_date": chunk.metadata["effective_date"],
            "chunk_index": chunk_index,
            "content": chunk.page_content,
        }

        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
        )

    upsert_chunks(points)

    return len(points)