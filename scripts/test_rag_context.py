from app.rag.retriever import retrieve
from app.rag.context import format_retrieved_context


def main():

    query = (
        "What happens if a customer cancels "
        "less than two hours before pickup?"
    )

    results = retrieve(
        query=query,
        top_k=5,
    )

    context = format_retrieved_context(results)

    print("=" * 70)
    print("RAG CONTEXT")
    print("=" * 70)

    print(context)


if __name__ == "__main__":
    main()