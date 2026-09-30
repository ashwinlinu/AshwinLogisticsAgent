from app.rag.retriever import retrieve


def main():

    query = (
        "What happens if a customer cancels "
        "less than two hours before pickup?"
    )

    print("=" * 70)
    print("QUERY")
    print("=" * 70)
    print(query)

    results = retrieve(
        query=query,
        top_k=5,
    )

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    for index, result in enumerate(results, start=1):

        print(f"\nRESULT {index}")
        print("-" * 70)

        print(f"Score: {result.score}")
        print(f"ID: {result.id}")

        payload = result.payload

        print(
            f"Document: "
            f"{payload.get('document_id')}"
        )

        print(
            f"Title: "
            f"{payload.get('title')}"
        )

        print(
            f"Category: "
            f"{payload.get('category')}"
        )

        print(
            f"Chunk: "
            f"{payload.get('chunk_index')}"
        )

        print("\nContent:")
        print(payload.get("content"))


if __name__ == "__main__":
    main()