from app.rag.loader import load_documents


def main():
    documents = load_documents("data/documents")

    print(f"Loaded documents: {len(documents)}")

    for document in documents:
        print("\n" + "=" * 60)

        print(f"Title: {document.metadata['title']}")
        print(f"ID: {document.metadata['document_id']}")
        print(f"Category: {document.metadata['category']}")
        print(f"Version: {document.metadata['version']}")
        print(f"Source: {document.metadata['source']}")
        print(
            f"Effective date: "
            f"{document.metadata['effective_date']}"
        )

        print(f"Content length: {len(document.page_content)}")


if __name__ == "__main__":
    main()