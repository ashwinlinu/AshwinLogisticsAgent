from app.rag.embeddings import embed_text


def main():
    text = "Ashwin Logistics shipment cancellation policy"

    vector = embed_text(text)

    print(f"Vector type: {type(vector)}")
    print(f"Vector dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")


if __name__ == "__main__":
    main()