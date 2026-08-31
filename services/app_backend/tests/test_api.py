import importlib
import os
from pathlib import Path

from fastapi.testclient import TestClient


def make_client(tmp_path: Path) -> TestClient:
    os.environ['APP_ENV'] = 'test'
    os.environ['DATABASE_URL'] = f"sqlite:///{tmp_path / 'test.db'}"
    os.environ['APP_JWT_SECRET'] = 'test-secret-that-is-long-enough-for-tests'
    os.environ['APP_ADMIN_PASSWORD'] = 'AdminPass123!'
    os.environ['APP_SEED_DEMO'] = 'true'
    import app.config as config
    import app.db as db
    import app.main as main
    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(main)
    return TestClient(main.app)


def login(client: TestClient, email: str = 'demo@brawlerzbox.com', password: str = 'DemoPass123!') -> dict:
    response = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
    assert response.status_code == 200, response.text
    return response.json()


def auth(tokens: dict) -> dict[str, str]:
    return {'Authorization': f"Bearer {tokens['accessToken']}"}


def test_health_and_login(tmp_path: Path):
    with make_client(tmp_path) as client:
        assert client.get('/healthz').status_code == 200
        tokens = login(client)
        assert tokens['accessToken']
        assert client.get('/api/v1/auth/me', headers=auth(tokens)).status_code == 200


def test_catalog_and_reservation(tmp_path: Path):
    with make_client(tmp_path) as client:
        tokens = login(client)
        headers = auth(tokens)
        classes = client.get('/api/v1/classes', headers=headers)
        assert classes.status_code == 200
        class_id = classes.json()[0]['id']
        reserved = client.post(f'/api/v1/classes/{class_id}/reserve', headers=headers)
        assert reserved.status_code == 200
        assert reserved.json()['isReserved'] is True
        cancelled = client.delete(f'/api/v1/classes/{class_id}/reserve', headers=headers)
        assert cancelled.status_code == 200
        assert cancelled.json()['isReserved'] is False


def test_nutrition_cart_and_qr(tmp_path: Path):
    with make_client(tmp_path) as client:
        member = login(client)
        member_headers = auth(member)
        nutrition = client.get('/api/v1/nutrition', headers=member_headers)
        assert nutrition.status_code == 200
        assert nutrition.json()['meals']
        products = client.get('/api/v1/supplements', headers=member_headers).json()
        cart = client.put(f"/api/v1/cart/{products[0]['id']}", headers=member_headers, json={'quantity': 2})
        assert cart.status_code == 200
        assert cart.json()['items'][0]['quantity'] == 2
        qr_pass = client.post('/api/v1/qr/pass', headers=member_headers, json={'ttlMinutes': 10})
        assert qr_pass.status_code == 201
        admin = login(client, 'admin@brawlerzbox.com', 'AdminPass123!')
        validated = client.post('/api/v1/qr/validate', headers=auth(admin), json={'token': qr_pass.json()['token']})
        assert validated.status_code == 200
        assert validated.json()['valid'] is True
