from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

_embedding_model = None


def _get_embedding_model():
    """Load the embedding model only when a vector operation needs it."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def embed_text(text: str) -> list[float]:
    vector = _get_embedding_model().encode(
        text,
        normalize_embeddings=True,
    )

    return vector.tolist()


def embed_documents(
    texts: list[str],
) -> list[list[float]]:
    vectors = _get_embedding_model().encode(
        texts,
        normalize_embeddings=True,
    )

    return vectors.tolist()
