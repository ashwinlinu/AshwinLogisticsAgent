from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)


def embed_text(text: str) -> list[float]:
    vector = embedding_model.encode(
        text,
        normalize_embeddings=True,
    )

    return vector.tolist()


def embed_documents(
    texts: list[str],
) -> list[list[float]]:
    vectors = embedding_model.encode(
        texts,
        normalize_embeddings=True,
    )

    return vectors.tolist()