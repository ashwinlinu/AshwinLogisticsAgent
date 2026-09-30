from app.rag.loader import load_documents
from app.rag.chunker import chunk_documents
from app.rag.ingestion import ingest_chunks


def main():
    documents = load_documents("data/documents")

    print(f"Documents loaded: {len(documents)}")

    chunks = chunk_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    count = ingest_chunks(chunks)

    print(f"Chunks ingested: {count}")


if __name__ == "__main__":
    main()