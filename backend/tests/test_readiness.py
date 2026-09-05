"""Governance readiness endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app


def test_readiness_is_admin_only_and_reports_model_state() -> None:
    with TestClient(app) as client:
        technician = client.post(
            "/api/auth/login",
            json={"email": "technician@fleetmind.demo", "password": "Service2026!"},
        )
        assert technician.status_code == 200
        technician_headers = {
            "Authorization": f"Bearer {technician.json()['access_token']}"
        }
        assert client.get("/api/admin/readiness", headers=technician_headers).status_code == 403

        manager = client.post(
            "/api/auth/login",
            json={"email": "manager@fleetmind.demo", "password": "FleetMind2026!"},
        )
        assert manager.status_code == 200
        manager_headers = {"Authorization": f"Bearer {manager.json()['access_token']}"}
        response = client.get("/api/admin/readiness", headers=manager_headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["predictive_model_status"] == "ready"
        assert "deterministic fleet analytics" in payload["grounding"]
        assert payload["llm_provider"] in {"demo", "bedrock"}
        assert payload["cors_origins"] >= 1
