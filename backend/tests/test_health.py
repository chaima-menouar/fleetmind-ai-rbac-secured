"""API, authentication, and role-authorization tests for demo mode."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def _login(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(scope="module")
def manager_headers(client: TestClient) -> dict[str, str]:
    return _login(client, "manager@fleetmind.demo", "FleetMind2026!")


@pytest.fixture(scope="module")
def technician_headers(client: TestClient) -> dict[str, str]:
    return _login(client, "technician@fleetmind.demo", "Service2026!")


@pytest.fixture(scope="module")
def viewer_headers(client: TestClient) -> dict[str, str]:
    return _login(client, "viewer@fleetmind.demo", "View2026!")


def test_health_is_public(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_endpoint_requires_signed_session(client: TestClient) -> None:
    assert client.get("/api/fleet/summary").status_code == 401
    tampered = client.get(
        "/api/fleet/summary",
        headers={"Authorization": "Bearer bad.token"},
    )
    assert tampered.status_code == 401


def test_company_accounts_receive_server_owned_roles(
    client: TestClient,
    manager_headers: dict[str, str],
    technician_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    expected = [
        (manager_headers, "admin"),
        (technician_headers, "technician"),
        (viewer_headers, "viewer"),
    ]
    for headers, role in expected:
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["role"] == role

    rejected = client.post(
        "/api/auth/login",
        json={"email": "manager@fleetmind.demo", "password": "wrong"},
    )
    assert rejected.status_code == 401


def test_viewer_registration_can_only_create_read_only_role(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register-viewer",
        json={
            "display_name": "Read Only User",
            "email": "readonly@example.com",
            "password": "SecureViewer1!",
            "verification_code": "482913",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["user"]["role"] == "viewer"
    headers = {"Authorization": f"Bearer {payload['access_token']}"}
    assert client.get("/api/fleet/summary", headers=headers).status_code == 200
    assert client.get("/api/admin/usage", headers=headers).status_code == 403


def test_viewer_is_read_only_at_api_boundary(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    assert client.get("/api/fleet/summary", headers=viewer_headers).status_code == 200
    assert client.get("/api/ml/model-card", headers=viewer_headers).status_code == 200
    assert client.get("/api/ml/samples", headers=viewer_headers).status_code == 403
    assert client.post(
        "/api/ml/predict",
        headers=viewer_headers,
        json={"sample_id": "test-example-01"},
    ).status_code == 403
    assert client.post(
        "/api/agents/run",
        headers=viewer_headers,
        json={"task_type": "maintenance_triage", "vehicle_id": "FM-4410"},
    ).status_code == 403
    assert client.get("/api/bots", headers=viewer_headers).status_code == 403
    assert client.post(
        "/api/chat/message",
        headers=viewer_headers,
        json={"bot_id": "technician", "content": "Hello"},
    ).status_code == 403


def test_technician_only_sees_approved_assistants(
    client: TestClient,
    technician_headers: dict[str, str],
) -> None:
    bots = client.get("/api/bots?shared_only=true", headers=technician_headers)
    assert bots.status_code == 200
    bot_ids = {bot["id"] for bot in bots.json()}
    assert "technician" in bot_ids
    assert "fleet-manager" not in bot_ids
    assert "sales-copilot" not in bot_ids

    forbidden = client.post(
        "/api/chat/message",
        headers=technician_headers,
        json={"bot_id": "fleet-manager", "content": "Show manager analysis"},
    )
    assert forbidden.status_code == 403


def test_technician_chat_and_conversation_ownership(
    client: TestClient,
    technician_headers: dict[str, str],
    manager_headers: dict[str, str],
) -> None:
    chat = client.post(
        "/api/chat/message",
        headers=technician_headers,
        json={"bot_id": "technician", "content": "Battery warning on vehicle FM-4410"},
    )
    assert chat.status_code == 200
    conversation_id = chat.json()["conversation_id"]
    history = client.get(f"/api/chat/history/{conversation_id}", headers=technician_headers)
    assert history.status_code == 200
    assert [message["role"] for message in history.json()["messages"]] == ["user", "assistant"]
    manager_history = client.get(
        f"/api/chat/history/{conversation_id}",
        headers=manager_headers,
    )
    assert manager_history.status_code == 403


def test_only_manager_can_create_assistants_and_upload_knowledge(
    client: TestClient,
    manager_headers: dict[str, str],
    technician_headers: dict[str, str],
) -> None:
    payload = {
        "name": "Warranty Assistant",
        "department": "support",
        "description": "Helps support agents explain enterprise fleet warranty coverage.",
        "system_prompt": "Answer warranty questions using only approved policy documents.",
        "is_shared": True,
    }
    assert client.post("/api/bots", headers=technician_headers, json=payload).status_code == 403
    created = client.post("/api/bots", headers=manager_headers, json=payload)
    assert created.status_code == 201

    rejected = client.post(
        f"/api/bots/{created.json()['id']}/knowledge",
        headers=manager_headers,
        files={"file": ("unsafe.exe", b"not allowed", "application/octet-stream")},
    )
    assert rejected.status_code == 400


def test_operator_fleet_agent_and_admin_boundary(
    client: TestClient,
    technician_headers: dict[str, str],
    manager_headers: dict[str, str],
) -> None:
    fleet = client.get("/api/fleet/summary", headers=technician_headers)
    assert fleet.status_code == 200
    assert fleet.json()["total_vehicles"] == 5

    task = client.post(
        "/api/agents/run",
        headers=technician_headers,
        json={"task_type": "maintenance_triage", "vehicle_id": "FM-4410"},
    )
    assert task.status_code == 200
    assert task.json()["output"]["ticket"]["status"] == "open"
    task_id = task.json()["task_id"]
    assert client.get(f"/api/agents/tasks/{task_id}", headers=technician_headers).status_code == 200
    assert client.get(f"/api/agents/tasks/{task_id}", headers=manager_headers).status_code == 200

    assert client.get("/api/admin/usage", headers=technician_headers).status_code == 403
    usage = client.get("/api/admin/usage", headers=manager_headers)
    assert usage.status_code == 200
    assert usage.json()["total_agent_runs"] >= 1


def test_real_aps_model_card_and_prediction(
    client: TestClient,
    technician_headers: dict[str, str],
) -> None:
    card = client.get("/api/ml/model-card", headers=technician_headers)
    assert card.status_code == 200
    payload = card.json()
    assert payload["dataset"]["name"] == "APS Failure at Scania Trucks"
    assert payload["dataset"]["test_rows"] == 16_000
    assert payload["metrics"]["recall"] > 0.9

    samples = client.get("/api/ml/samples", headers=technician_headers)
    assert samples.status_code == 200
    sample_id = samples.json()[0]["sample_id"]
    prediction = client.post(
        "/api/ml/predict",
        headers=technician_headers,
        json={"sample_id": sample_id},
    )
    assert prediction.status_code == 200
    assert prediction.json()["sample_id"] == sample_id


def test_manager_can_use_manager_assistant(
    client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/chat/message",
        headers=manager_headers,
        json={
            "bot_id": "fleet-manager",
            "content": "Which vehicles need maintenance this week?",
        },
    )
    assert response.status_code == 200
    assert "FM-4410" in response.json()["content"]
