from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config.settings import settings


VECTOR_SIZE = 384


qdrant_client = QdrantClient(
    url=settings.qdrant_url,
)


def create_collection() -> None:
    existing_collections = qdrant_client.get_collections().collections

    collection_names = {
        collection.name
        for collection in existing_collections
    }

    if settings.qdrant_collection in collection_names:
        print(
            f"Collection already exists: "
            f"{settings.qdrant_collection}"
        )
        return

    qdrant_client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print(
        f"Created collection: "
        f"{settings.qdrant_collection}"
    )


def upsert_chunks(
    points: list[PointStruct],
) -> None:
    qdrant_client.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
    )