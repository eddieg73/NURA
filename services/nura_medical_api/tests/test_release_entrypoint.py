import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def make_client(tmp_path: Path) -> TestClient:
    os.environ.update(
        {
            "APP_ENV": "test",
            "DATABASE_URL": f"sqlite:///{tmp_path / 'release.db'}",
            "JWT_SECRET": "release-test-secret-with-more-than-thirty-two-characters",
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
    import app.release_entrypoint as release

    importlib.reload(release)
    return TestClient(release.app)


def register(client: TestClient, email: str, organization: str) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "ClinicalPass123!",
            "full_name": email.split('@')[0],
            "organization_name": organization,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def headers(tokens: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_export_contains_only_authenticated_users_drafts(tmp_path: Path):
    with make_client(tmp_path) as client:
        first = register(client, "first@example.com", "First Clinic")
        second = register(client, "second@example.com", "Second Clinic")

        first_draft = client.post(
            "/api/v1/clinical/drafts",
            headers=headers(first),
            json={
                "operation": "scribe",
                "case_text": "First clinician source text.",
                "consent_attested": True,
            },
        )
        second_draft = client.post(
            "/api/v1/clinical/drafts",
            headers=headers(second),
            json={
                "operation": "scribe",
                "case_text": "Second clinician source text.",
                "consent_attested": True,
            },
        )
        assert first_draft.status_code == 200
        assert second_draft.status_code == 200

        export = client.get("/api/v1/account/export", headers=headers(first))
        assert export.status_code == 200
        body = export.json()
        assert len(body["clinical_drafts"]) == 1
        assert body["clinical_drafts"][0]["id"] == first_draft.json()["id"]
