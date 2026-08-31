import importlib
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def runtime(tmp_path: Path):
    os.environ.update(
        {
            "APP_ENV": "test",
            "DATABASE_URL": f"sqlite:///{tmp_path / 'nura-medical.db'}",
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
    with TestClient(main.app) as client:
        yield main, client


def register(client: TestClient, email: str = "clinician@example.com") -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "ClinicalPass123!",
            "full_name": "Test Clinician",
            "organization_name": "Shared Test Clinic",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def login(client: TestClient, email: str, password: str = "ClinicalPass123!") -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "device_label": "pytest",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def headers(tokens: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def add_user(main, organization_id: str, email: str, role: str) -> None:
    from app.models import User
    from app.security import hash_password

    with main.SessionLocal() as db:
        db.add(
            User(
                organization_id=organization_id,
                email=email,
                full_name=email.split("@")[0],
                password_hash=hash_password("ClinicalPass123!"),
                role=role,
            )
        )
        db.commit()


def create_draft(client: TestClient, tokens: dict, source_text: str) -> dict:
    response = client.post(
        "/api/v1/clinical/drafts",
        headers=headers(tokens),
        json={
            "operation": "synthesis",
            "case_text": source_text,
            "patient_reference": "DEIDENTIFIED-001",
            "consent_attested": True,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_health_login_refresh_and_legal(runtime):
    _main, client = runtime
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 200
    legal = client.get("/api/v1/legal")
    assert legal.status_code == 200
    assert legal.json()["account_deletion_available"] is True

    tokens = register(client)
    me = client.get("/api/v1/account/me", headers=headers(tokens))
    assert me.status_code == 200
    assert me.json()["role"] == "clinician"

    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": tokens["refresh_token"],
            "device_label": "pytest-refreshed",
        },
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != tokens["refresh_token"]
    replay = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert replay.status_code == 401


def test_clinical_consent_safe_mode_and_reviewer_gate(runtime):
    main, client = runtime
    clinician = register(client)
    organization_id = clinician["user"]["organization_id"]
    add_user(main, organization_id, "reviewer@example.com", "reviewer")
    reviewer = login(client, "reviewer@example.com")

    denied = client.post(
        "/api/v1/clinical/drafts",
        headers=headers(clinician),
        json={
            "operation": "dx",
            "case_text": "Adult with chest discomfort. Vital signs were not supplied.",
            "consent_attested": False,
        },
    )
    assert denied.status_code == 422

    draft = create_draft(
        client,
        clinician,
        "Adult with chest discomfort. Vital signs were not supplied.",
    )
    assert draft["status"] == "draft"
    assert draft["provider_approval_required"] is True
    assert draft["provider_name"] == "disabled-safe-mode"
    assert draft["output"]["confidence"] == "low"
    assert draft["output"]["urgency"] == "undetermined"
    assert draft["output"]["missing_data"]
    assert draft["output"]["limitations"]

    clinician_review = client.post(
        f"/api/v1/clinical/drafts/{draft['id']}/review",
        headers=headers(clinician),
        json={"status": "approved", "comment": "not permitted"},
    )
    assert clinician_review.status_code == 403

    reviewer_queue = client.get(
        "/api/v1/clinical/drafts",
        headers=headers(reviewer),
    )
    assert reviewer_queue.status_code == 200
    assert reviewer_queue.json()[0]["id"] == draft["id"]

    approved = client.post(
        f"/api/v1/clinical/drafts/{draft['id']}/review",
        headers=headers(reviewer),
        json={"status": "approved", "comment": "Independent review completed"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["reviewed_by"] == reviewer["user"]["id"]


def test_same_organization_clinicians_cannot_read_or_export_each_other(runtime):
    main, client = runtime
    first = register(client, "first@example.com")
    organization_id = first["user"]["organization_id"]
    add_user(main, organization_id, "second@example.com", "clinician")
    second = login(client, "second@example.com")

    first_draft = create_draft(client, first, "First clinician source text.")
    second_draft = create_draft(client, second, "Second clinician source text.")

    first_list = client.get("/api/v1/clinical/drafts", headers=headers(first))
    second_list = client.get("/api/v1/clinical/drafts", headers=headers(second))
    assert [row["id"] for row in first_list.json()] == [first_draft["id"]]
    assert [row["id"] for row in second_list.json()] == [second_draft["id"]]

    hidden = client.get(
        f"/api/v1/clinical/drafts/{second_draft['id']}",
        headers=headers(first),
    )
    assert hidden.status_code == 404

    first_export = client.get("/api/v1/account/export", headers=headers(first))
    second_export = client.get("/api/v1/account/export", headers=headers(second))
    assert [row["id"] for row in first_export.json()["clinical_drafts"]] == [
        first_draft["id"]
    ]
    assert [row["id"] for row in second_export.json()["clinical_drafts"]] == [
        second_draft["id"]
    ]


def test_tasks_export_and_account_deletion(runtime):
    _main, client = runtime
    tokens = register(client)
    created = client.post(
        "/api/v1/ops/tasks",
        headers=headers(tokens),
        json={"title": "Review draft", "priority": "high"},
    )
    assert created.status_code == 200
    task_id = created.json()["id"]
    completed = client.patch(
        f"/api/v1/ops/tasks/{task_id}",
        headers=headers(tokens),
        json={"status": "completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["completed_at"] is not None

    exported = client.get("/api/v1/account/export", headers=headers(tokens))
    assert exported.status_code == 200
    assert exported.json()["tasks"][0]["id"] == task_id

    deleted = client.request(
        "DELETE",
        "/api/v1/account",
        headers=headers(tokens),
        json={"password": "ClinicalPass123!", "confirmation": "DELETE"},
    )
    assert deleted.status_code == 204
    assert client.get("/api/v1/account/me", headers=headers(tokens)).status_code == 401


def test_production_configuration_rejects_unsafe_defaults():
    from app.config import Settings

    unsafe = Settings(
        app_env="production",
        database_url="sqlite:///unsafe.db",
        jwt_secret="change-me",
        allowed_origins="*",
    )
    with pytest.raises(RuntimeError):
        unsafe.validate_for_startup()
