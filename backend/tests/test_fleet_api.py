"""API coverage for authenticated deterministic fleet intelligence."""

from fastapi.testclient import TestClient

from app.main import app


def _login(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_fleet_intelligence_requires_authentication() -> None:
    with TestClient(app) as client:
        assert client.get("/api/fleet/intelligence").status_code == 401


def test_fleet_intelligence_exposes_verified_risk_ranking() -> None:
    with TestClient(app) as client:
        headers = _login(client, "manager@fleetmind.demo", "FleetMind2026!")
        response = client.get("/api/fleet/intelligence", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["generated_from"] == "deterministic_fleet_analytics"
    assert payload["risk_ranking"][0]["vehicle_id"] == "FM-4410"
    assert payload["risk_ranking"][0]["risk_score"] >= 60
    assert "FM-4410" in payload["critical_vehicle_ids"]
    assert {item["label"] for item in payload["kpis"]} >= {
        "Availability",
        "Average health",
        "Service due <=7d",
    }


def test_viewer_can_read_intelligence_but_not_run_triage() -> None:
    with TestClient(app) as client:
        headers = _login(client, "viewer@fleetmind.demo", "View2026!")
        intelligence = client.get("/api/fleet/intelligence", headers=headers)
        triage = client.post(
            "/api/agents/run",
            headers=headers,
            json={"task_type": "maintenance_triage", "vehicle_id": "FM-4410"},
        )

    assert intelligence.status_code == 200
    assert triage.status_code == 403
