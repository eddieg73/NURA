import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def build_client(tmp_path: Path):
    os.environ.update(
        {
            "APP_ENV": "test",
            "DATABASE_URL": f"sqlite:///{tmp_path / 'same-org.db'}",
            "JWT_SECRET": "same-org-test-secret-with-more-than-thirty-two-characters",
            "ALLOWED_ORIGINS": "http://localhost:8080",
            "ALLOW_SELF_REGISTRATION": "false",
            "SEED_DEMO_DATA": "false",
            "AI_PROVIDER": "disabled",
        }
    )
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]

    import app.config as config

    config.get_settings.cache_clear()
    import app.release_entrypoint as release

    importlib.reload(release)
    return release, TestClient(release.app)


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_two_clinicians_in_one_org_receive_separate_exports(tmp_path: Path):
    release, client = build_client(tmp_path)
    with client:
        from app.models import Organization, User
        from app.security import hash_password

        with release.main.SessionLocal() as db:
            organization = Organization(name="Shared Clinical Organization")
            db.add(organization)
            db.flush()
            first = User(
                organization_id=organization.id,
                email="first.shared@example.com",
                full_name="First Shared Clinician",
                password_hash=hash_password("ClinicalPass123!"),
                role="clinician",
            )
            second = User(
                organization_id=organization.id,
                email="second.shared@example.com",
                full_name="Second Shared Clinician",
                password_hash=hash_password("ClinicalPass123!"),
                role="clinician",
            )
            db.add_all([first, second])
            db.commit()

        first_login = client.post(
            "/api/v1/auth/login",
            json={
                "email": "first.shared@example.com",
                "password": "ClinicalPass123!",
                "device_label": "pytest-first",
            },
        )
        second_login = client.post(
            "/api/v1/auth/login",
            json={
                "email": "second.shared@example.com",
                "password": "ClinicalPass123!",
                "device_label": "pytest-second",
            },
        )
        assert first_login.status_code == 200
        assert second_login.status_code == 200

        first_headers = bearer(first_login.json()["access_token"])
        second_headers = bearer(second_login.json()["access_token"])

        first_draft = client.post(
            "/api/v1/clinical/drafts",
            headers=first_headers,
            json={
                "operation": "scribe",
                "case_text": "First clinician source text.",
                "consent_attested": True,
            },
        )
        second_draft = client.post(
            "/api/v1/clinical/drafts",
            headers=second_headers,
            json={
                "operation": "scribe",
                "case_text": "Second clinician source text.",
                "consent_attested": True,
            },
        )
        assert first_draft.status_code == 200
        assert second_draft.status_code == 200

        first_export = client.get(
            "/api/v1/account/export",
            headers=first_headers,
        )
        second_export = client.get(
            "/api/v1/account/export",
            headers=second_headers,
        )
        assert first_export.status_code == 200
        assert second_export.status_code == 200
        assert [item["id"] for item in first_export.json()["clinical_drafts"]] == [
            first_draft.json()["id"]
        ]
        assert [item["id"] for item in second_export.json()["clinical_drafts"]] == [
            second_draft.json()["id"]
        ]
