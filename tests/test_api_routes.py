import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api import routes
from app.api.auth import current_identity
from app.api.models import BookingCreate, ChatRequest, CustomerCreate, CustomerUpdate, LoginRequest, RegisterRequest, ShipmentCreate
from app.db.repositories import auth_repository as auth_repository_module
from app.db.repositories import conversation_repository as conversation_repository_module
from app.db.repositories import operations_repository as operations_repository_module


IDENTITY = {
    "user": {"user_id": "USR-A", "email": "owner@example.com", "full_name": "Owner", "role": "admin", "status": "active"},
    "session": {"session_id": "AUTH-SESSION-A", "user_id": "USR-A", "is_active": True},
}


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, timeout=5))


def request():
    return Request({
        "type": "http", "http_version": "1.1", "method": "POST", "scheme": "http",
        "path": "/test", "raw_path": b"/test", "query_string": b"", "headers": [],
        "client": ("127.0.0.1", 1234), "server": ("test", 80),
    })


def async_return(value):
    async def fn(*args, **kwargs):
        return value
    return fn


def capture(calls, return_value=None):
    async def fn(*args, **kwargs):
        calls.append(args)
        return return_value
    return fn


def test_register_creates_operator_account_and_session(monkeypatch):
    user = {"user_id": "USR-NEW", "email": "new@example.com", "full_name": "New User", "role": "operator", "status": "active"}
    session = {"session_id": "AUTH-NEW", "user_id": "USR-NEW", "is_active": True}
    audits = []
    monkeypatch.setattr(auth_repository_module.auth_repository, "register", async_return(user))
    monkeypatch.setattr(auth_repository_module.auth_repository, "create_session", async_return(("secret-token", session)))
    monkeypatch.setattr(routes, "record_audit", capture(audits))
    routes._auth_attempts.clear()

    result = run(routes.register(RegisterRequest(email=" NEW@example.com ", password="long-passphrase1", full_name="New User"), request()))
    assert result["access_token"] == "secret-token"
    assert result["user"]["role"] == "operator"
    assert [audit[1] for audit in audits] == ["account.register", "session.create"]


def test_registration_validates_password_and_email():
    with pytest.raises(ValueError):
        RegisterRequest(email="not-an-email", password="long-passphrase1", full_name="A")
    with pytest.raises(ValueError):
        RegisterRequest(email="a@example.com", password="short", full_name="A")


def test_login_allocates_session(monkeypatch):
    user = {"user_id": "USR-A", "email": "owner@example.com", "role": "admin"}
    session = {"session_id": "AUTH-LOGIN", "user_id": "USR-A", "is_active": True}
    monkeypatch.setattr(auth_repository_module.auth_repository, "authenticate", async_return(user))
    monkeypatch.setattr(auth_repository_module.auth_repository, "create_session", async_return(("login-token", session)))
    monkeypatch.setattr(routes, "record_audit", async_return(None))
    routes._auth_attempts.clear()
    result = run(routes.login(LoginRequest(email="OWNER@example.com", password="correct-password"), request()))
    assert result["session"]["session_id"] == "AUTH-LOGIN"
    assert result["token_type"] == "bearer"


def test_invalid_login_is_rejected(monkeypatch):
    monkeypatch.setattr(auth_repository_module.auth_repository, "authenticate", async_return(None))
    routes._auth_attempts.clear()
    with pytest.raises(HTTPException) as error:
        run(routes.login(LoginRequest(email="owner@example.com", password="bad"), request()))
    assert error.value.status_code == 401


def test_auth_throttle_rejects_excess_attempts():
    routes._auth_attempts.clear()
    for _ in range(10):
        routes._limit_auth_attempts(request())
    with pytest.raises(HTTPException) as error:
        routes._limit_auth_attempts(request())
    assert error.value.status_code == 429
    routes._auth_attempts.clear()


def test_current_identity_rejects_missing_or_expired_token(monkeypatch):
    monkeypatch.setattr(auth_repository_module.auth_repository, "get_user_for_token", async_return(None))
    with pytest.raises(HTTPException) as error:
        run(current_identity(None))
    assert error.value.status_code == 401


def test_customer_create_uses_authenticated_owner(monkeypatch):
    created = {"customer_id": "CUS-1", "user_id": "USR-A", "name": "Nisha"}
    calls, audits = [], []
    monkeypatch.setattr(operations_repository_module.operations_repository, "create_customer", capture(calls, created))
    monkeypatch.setattr(routes, "record_audit", capture(audits))
    result = run(routes.create_customer(CustomerCreate(name="Nisha"), IDENTITY))
    assert calls[0][0] == "USR-A"
    assert result["user_id"] == "USR-A"
    assert audits[0][1] == "customer.create"


def test_customer_get_hides_non_owned_record(monkeypatch):
    calls = []
    monkeypatch.setattr(operations_repository_module.operations_repository, "get_customer", capture(calls, None))
    with pytest.raises(HTTPException) as error:
        run(routes.get_customer("CUS-OTHER", IDENTITY))
    assert error.value.status_code == 404
    assert calls == [("USR-A", "CUS-OTHER")]


def test_customer_update_and_delete_enforce_owner_and_booking_integrity(monkeypatch):
    calls = []
    monkeypatch.setattr(operations_repository_module.operations_repository, "update_customer", capture(calls, None))
    monkeypatch.setattr(operations_repository_module.operations_repository, "delete_customer", capture(calls, False))
    monkeypatch.setattr(operations_repository_module.operations_repository, "get_customer", capture(calls, {"customer_id": "CUS-1"}))
    with pytest.raises(HTTPException) as update_error:
        run(routes.update_customer("CUS-1", CustomerUpdate(name="New"), IDENTITY))
    with pytest.raises(HTTPException) as delete_error:
        run(routes.delete_customer("CUS-1", IDENTITY))
    assert update_error.value.status_code == 404
    assert delete_error.value.status_code == 409
    assert all(call[0] == "USR-A" for call in calls)


def test_booking_and_shipment_create_are_owner_scoped(monkeypatch):
    calls = []
    monkeypatch.setattr(operations_repository_module.operations_repository, "create_booking", capture(calls, None))
    monkeypatch.setattr(operations_repository_module.operations_repository, "create_shipment", capture(calls, None))
    with pytest.raises(HTTPException) as booking_error:
        run(routes.create_booking(BookingCreate(customer_id="CUS-OTHER", pickup_location="A", destination="B", service_type="Express"), IDENTITY))
    with pytest.raises(HTTPException) as shipment_error:
        run(routes.create_shipment(ShipmentCreate(booking_id="BKG-OTHER", origin="A", destination="B", carrier="Carrier"), IDENTITY))
    assert booking_error.value.status_code == shipment_error.value.status_code == 404
    assert calls[0][0] == calls[1][0] == "USR-A"


def test_shipment_lookup_and_list_are_owner_scoped(monkeypatch):
    calls = []
    monkeypatch.setattr(operations_repository_module.operations_repository, "get_shipment", capture(calls, None))
    monkeypatch.setattr(operations_repository_module.operations_repository, "list_shipments", capture(calls, []))
    with pytest.raises(HTTPException) as error:
        run(routes.get_shipment("SHP-123456", request(), IDENTITY))
    result = run(routes.list_shipments(identity=IDENTITY))
    assert error.value.status_code == 404
    assert result == {"shipments": []}
    assert calls == [("USR-A", "SHP-123456"), ("USR-A", None)]


def test_chat_uses_authenticated_user_and_login_session(monkeypatch):
    monkeypatch.setattr(conversation_repository_module.conversation_repository, "get_conversation", async_return(None))
    monkeypatch.setattr(conversation_repository_module.conversation_repository, "get_session", async_return(None))
    monkeypatch.setattr(conversation_repository_module.conversation_repository, "get_conversation", async_return(SimpleNamespace(conversation_id="CONV-EXISTING", session_id="THREAD-1")))
    monkeypatch.setattr(routes, "record_audit", async_return(None))
    generated = []
    async def generate(*args, **kwargs):
        generated.append(kwargs)
        return "Hello", "CONV-1"
    monkeypatch.setattr(routes.ai_service, "generate_response", generate)
    result = run(routes.chat(ChatRequest(message="Hello"), request(), IDENTITY))
    assert result.conversation_id == "CONV-1"
    assert generated[0]["user_id"] == "USR-A"
    assert generated[0]["auth_session_id"] == "AUTH-SESSION-A"
