import importlib
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path):
    db_path = tmp_path / "nura-medical-test.db"
    os.environ.update(
        {
            "APP_ENV": "test",
            "DATABASE_URL": f"sqlite:///{db_path}",
            "JWT_SECRET": "test-secret-with-more-than-thirty-two-characters",
            "ALLOWED_ORIGINS": "http://localhost:8080",
            "ALLOW_SELF_REGISTRATION": "true",
            "SEED_DEMO_DATA": "false",
            "AI_PROVIDER": "disabled",
        }
    )
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]
    import app.config as config

    config.get_settings.cache_clear()
    import app.main as main

    importlib.reload(main)
    with TestClient(main.app) as test_client:
        yield test_client


def register(client: TestClient, email: str = "clinician@example.com") -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "ClinicalPass123!",
            "full_name": "Test Clinician",
            "organization_name": "Test Clinic",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def auth_headers(tokens: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_health_auth_refresh_and_me(client: TestClient):
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 200
    tokens = register(client)
    me = client.get("/api/v1/account/me", headers=auth_headers(tokens))
    assert me.status_code == 200
    assert me.json()["role"] == "clinician"
    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"], "device_label": "pytest"},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != tokens["refresh_token"]


def test_clinical_draft_is_safe_and_requires_review(client: TestClient):
    tokens = register(client)
    headers = auth_headers(tokens)
    denied = client.post(
        "/api/v1/clinical/drafts",
        headers=headers,
        json={
            "operation": "dx",
            "case_text": "Adult with chest discomfort. Vital signs were not supplied.",
            "consent_attested": False,
        },
    )
    assert denied.status_code == 422

    response = client.post(
        "/api/v1/clinical/drafts",
        headers=headers,
        json={
            "operation": "dx",
            "case_text": "Adult with chest discomfort. Vital signs were not supplied.",
            "consent_attested": True,
            "patient_reference": "DEIDENTIFIED-001",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "draft"
    assert body["provider_approval_required"] is True
    assert body["output"]["confidence"] == "low"
    assert body["output"]["urgency"] == "undetermined"

    forbidden = client.post(
        f"/api/v1/clinical/drafts/{body['id']}/review",
        headers=headers,
        json={"status": "approved", "comment": "reviewed"},
    )
    assert forbidden.status_code == 403


def test_tasks_export_and_account_deletion(client: TestClient):
    tokens = register(client)
    headers = auth_headers(tokens)
    created = client.post(
        "/api/v1/ops/tasks",
        headers=headers,
        json={"title": "Review draft", "priority": "high"},
    )
    assert created.status_code == 200
    task_id = created.json()["id"]
    completed = client.patch(
        f"/api/v1/ops/tasks/{task_id}",
        headers=headers,
        json={"status": "completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["completed_at"] is not None

    exported = client.get("/api/v1/account/export", headers=headers)
    assert exported.status_code == 200
    assert exported.json()["tasks"][0]["id"] == task_id

    deleted = client.request(
        "DELETE",
        "/api/v1/account",
        headers=headers,
        json={"password": "ClinicalPass123!", "confirmation": "DELETE"},
    )
    assert deleted.status_code == 204
    assert client.get("/api/v1/account/me", headers=headers).status_code == 401
