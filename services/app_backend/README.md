# Flutter App Backend

Persistent FastAPI backend for the Brawlerz Box Flutter MVP currently stored in `eddieg73/NURA`.

## Implemented

- Email/password registration and login
- Argon2 password hashing
- Short-lived JWT access tokens and revocable refresh sessions
- Per-user metrics, progress, nutrition, meals and wearable connection state
- Class catalog, capacity-aware reservations and cancellation
- Workout and supplement catalogs
- Persistent cart and order creation
- Expiring QR access passes, admin validation and check-in history
- Admin summary and catalog-create endpoints
- AI-coach contract that explicitly returns a non-model placeholder until a validated model is connected
- PostgreSQL production configuration and SQLite local/test configuration
- Health/readiness endpoints, CORS, request IDs and container health checks
- Automated API tests

## Run locally

```bash
cp .env.example .env
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Open API documentation at `http://127.0.0.1:8080/docs`.

For the demo seed, use:

- Member: `demo@brawlerzbox.com` / `DemoPass123!`
- Administrator: the values in `APP_ADMIN_EMAIL` and `APP_ADMIN_PASSWORD`

Do not use demo credentials in production.

## Docker

```bash
cp .env.example .env
# Replace every secret in .env
docker compose up --build -d
curl http://127.0.0.1:8080/readyz
```

The Compose file binds the API to loopback only. Put it behind the existing TLS reverse proxy after inspecting the VPS for port and route conflicts.

## Flutter configuration

Build the Flutter app with the deployed API base URL:

```bash
flutter run --dart-define=API_BASE_URL=https://api.example.com
```

The mobile client should never contain database credentials, JWT signing secrets or administrator passwords.

## Production gates

- Set a unique `APP_JWT_SECRET` of at least 32 random characters.
- Replace the administrator password and disable demo seeding.
- Restrict CORS to approved web origins.
- Terminate TLS at the reverse proxy and keep the application port private.
- Add Alembic-managed schema migrations before the first production schema change.
- Add rate limiting and centralized audit/monitoring at the gateway.
- Connect Apple/Google sign-in only after configuring and validating their server-side token verification.
- The AI-coach endpoint performs no model, diagnostic or medical inference in this build.
