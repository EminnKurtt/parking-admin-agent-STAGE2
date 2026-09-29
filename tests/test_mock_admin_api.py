import pytest
from fastapi.testclient import TestClient
from app.main import app, admin_requests

client = TestClient(app)
API_KEY = "secret-admin-key"


@pytest.fixture(autouse=True)
def clear_requests():
    """Ensures a clean state before and after each test."""
    admin_requests.clear()
    yield
    admin_requests.clear()


def test_unauthorized_access():
    """Requests without a valid API key should be rejected with 403."""
    response = client.post(
        "/admin/requests",
        json={
            "request_id": "REQ-001",
            "user_name": "John",
            "car_number": "ABC-123",
            "reservation_period": "2H",
            "formatted_message": "Test",
            "status": "PENDING"
        },
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 403


def test_create_and_approve_flow():
    """Creates a request and approves it end-to-end."""
    headers = {"X-API-Key": API_KEY}

    create_response = client.post(
        "/admin/requests",
        json={
            "request_id": "REQ-TEST1",
            "user_name": "Alice",
            "car_number": "XYZ-987",
            "reservation_period": "1 Day",
            "formatted_message": "Please approve.",
            "status": "PENDING"
        },
        headers=headers
    )
    assert create_response.status_code == 200
    assert create_response.json()["request_id"] == "REQ-TEST1"

    status_response = client.get("/admin/status/REQ-TEST1", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "PENDING"

    approve_response = client.post("/admin/approve/REQ-TEST1?action=APPROVED", headers=headers)
    assert approve_response.status_code == 200
    assert approve_response.json()["new_status"] == "APPROVED"

    status_response = client.get("/admin/status/REQ-TEST1", headers=headers)
    assert status_response.json()["status"] == "APPROVED"
