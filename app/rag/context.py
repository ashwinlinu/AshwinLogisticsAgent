from qdrant_client.models import ScoredPoint


def format_retrieved_context(
    results: list[ScoredPoint],
) -> str:

    context_parts = []

    for index, result in enumerate(results, start=1):

        payload = result.payload

        context_parts.append(
                        f"""
            SOURCE {index}

            Document: {payload.get("title")}
            Category: {payload.get("category")}
            Document ID: {payload.get("document_id")}
            Chunk: {payload.get("chunk_index")}
            Relevance Score: {result.score}

            Content:
            {payload.get("content")}
            """.strip()
        )

    return "\n\n---\n\n".join(context_parts)