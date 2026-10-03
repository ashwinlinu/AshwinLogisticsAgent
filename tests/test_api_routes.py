from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "request_id" in payload


def test_chat_with_valid_payload():
    response = client.post(
        "/ai/chat",
        json={"message": "Who are you?", "user_id": "ashwinlinu"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "response" in payload
    assert payload["conversation_id"] is not None


def test_chat_validation_rejects_empty_message():
    response = client.post(
        "/ai/chat",
        json={"message": "   ", "user_id": "ashwinlinu"},
    )
    assert response.status_code == 422


def test_shipment_lookup_returns_valid_response():
    response = client.get("/shipments/SHP-1001")
    assert response.status_code == 200
    payload = response.json()
    assert payload["shipment_id"] == "SHP-1001"
    assert payload["status"] == "ok"


def test_shipment_lookup_invalid_id():
    response = client.get("/shipments/ABC-123")
    assert response.status_code == 400
    payload = response.json()
    assert payload["message"] == "Invalid shipment ID format. Example: SHP-1001"
