from qdrant_client.models import ScoredPoint

from app.rag.embeddings import embed_text
from app.rag.vector_store import qdrant_client
from app.config.settings import settings


def retrieve(
    query: str,
    top_k: int = 5,
) -> list[ScoredPoint]:

    query_vector = embed_text(query)

    results = qdrant_client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    return results.points