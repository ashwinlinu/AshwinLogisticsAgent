from app.config.settings import settings
from app.rag.vector_store import qdrant_client


def main():
    collection_name = settings.qdrant_collection

    collection_info = qdrant_client.get_collection(
        collection_name=collection_name
    )

    print("=" * 60)
    print("QDRANT COLLECTION")
    print("=" * 60)

    print(f"Name: {collection_name}")
    print(f"Points: {collection_info.points_count}")

    print("\nVector configuration:")
    print(collection_info.config.params.vectors)

    print("\n" + "=" * 60)
    print("SAMPLE POINT")
    print("=" * 60)

    points, _ = qdrant_client.scroll(
        collection_name=collection_name,
        limit=1,
        with_payload=True,
        with_vectors=True,
    )

    if not points:
        print("No points found.")
        return

    point = points[0]

    print(f"ID: {point.id}")
    print(f"Vector dimensions: {len(point.vector)}")
    print("\nPayload:")
    print(point.payload)


if __name__ == "__main__":
    main()