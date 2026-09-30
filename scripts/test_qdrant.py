from app.rag.vector_store import qdrant_client


def main():
    collections = qdrant_client.get_collections()

    print("Connected to Qdrant")
    print(f"Collections: {collections}")


if __name__ == "__main__":
    main()