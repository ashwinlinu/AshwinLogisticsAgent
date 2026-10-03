from __future__ import annotations

import logging

from langchain_core.tools import tool

from app.rag.context import format_retrieved_context
from app.rag.retriever import retrieve

logger = logging.getLogger(__name__)


@tool
async def search_internal_knowledge(query: str) -> dict:
    """
    Lightweight tool wrapper that returns formatted retrieved context
    for a given query using the existing RAG retriever and context
    formatter.

    Returns a dictionary with the query, formatted context, and
    the number of results.
    """
    try:
        if query is None or not str(query).strip():
            return {
                "status": "invalid_input",
                "message": "Please provide a valid question for internal knowledge lookup.",
            }

        results = retrieve(query=str(query).strip(), top_k=5)

        if not results:
            return {
                "status": "no_results",
                "query": str(query).strip(),
                "message": "I couldn't find relevant internal policy information for that question.",
            }

        context = format_retrieved_context(results)

        return {
            "status": "ok",
            "query": str(query).strip(),
            "results_count": len(results),
            "context": context,
        }

    except Exception:
        logger.exception("RAG knowledge lookup failed")
        return {
            "status": "error",
            "query": str(query).strip() if isinstance(query, str) else query,
            "message": "I’m unable to access the policy knowledge base right now.",
        }
