from collections import Counter
from app.rag.loader import load_documents
from app.rag.chunker import chunk_documents


def main():
    documents = load_documents("data/documents")

    chunks = chunk_documents(documents)
    chunk_distribution = Counter(
    chunk.metadata["document_id"]
        for chunk in chunks
    )

    print("\nChunk distribution:")
    for document_id, count in chunk_distribution.items():
        print(f"{document_id}: {count} chunks")

    print(f"Documents loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print("\nFIRST CHUNK STRUCTURE")
    print(chunks[0])

    # print("\n" + "=" * 70)

    # for index, chunk in enumerate(chunks[:10], start=1):
    #     print(f"\nCHUNK {index}")
    #     print("-" * 70)

    #     print(f"Document ID: {chunk.metadata['document_id']}")
    #     print(f"Category: {chunk.metadata['category']}")
    #     print(f"Characters: {len(chunk.page_content)}")

    #     print("\nContent:")
    #     print(chunk.page_content[:500])


if __name__ == "__main__":
    main()