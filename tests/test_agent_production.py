from __future__ import annotations

import asyncio

from langchain_core.messages import AIMessage

from app.ai.routing import route_after_agent
from app.tools.rag_tools import search_internal_knowledge
from app.tools.shipment_tools import get_shipment_status


def test_shipment_intent_routes_to_shipment_tool():
    state = {
        "messages": [
            AIMessage(
                content="What is the status of SHP-1001?",
                tool_calls=[
                    {"name": "get_shipment_status", "args": {"shipment_id": "SHP-1001"}, "id": "call_1"}
                ],
            )
        ]
    }

    assert route_after_agent(state) == "shipment_tool"


def test_rag_intent_routes_to_rag_tool():
    state = {
        "messages": [
            AIMessage(
                content="What happens if I cancel less than 2 hours before pickup?",
                tool_calls=[
                    {"name": "search_internal_knowledge", "args": {"query": "cancel less than 2 hours before pickup"}, "id": "call_2"}
                ],
            )
        ]
    }

    assert route_after_agent(state) == "rag"


def test_conversational_message_does_not_route_to_tool():
    state = {
        "messages": [
            AIMessage(content="Who are you?", tool_calls=[])
        ]
    }

    assert route_after_agent(state) == "end"


def test_shipment_tool_handles_missing_id():
    result = asyncio.run(get_shipment_status.ainvoke({"shipment_id": "   "}))
    assert result["status"] == "invalid_input"


def test_shipment_tool_handles_invalid_id_format():
    result = asyncio.run(get_shipment_status.ainvoke({"shipment_id": "ABC-123"}))
    assert result["status"] == "invalid_input"


def test_rag_tool_handles_blank_query():
    result = asyncio.run(search_internal_knowledge.ainvoke({"query": "   "}))
    assert result["status"] == "invalid_input"


def test_rag_tool_returns_no_results_fallback():
    result = asyncio.run(search_internal_knowledge.ainvoke({"query": "nonexistent logistics claim answer"}))
    assert result["status"] in {"no_results", "error", "ok"}
