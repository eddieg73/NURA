from __future__ import annotations

import os
from dataclasses import dataclass


def _csv(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(',') if item.strip()]


@dataclass(frozen=True)
class Settings:
    env: str = os.getenv('APP_ENV', 'development').lower()
    database_url: str = os.getenv('DATABASE_URL', 'sqlite:///./nura_app.db')
    jwt_secret: str = os.getenv('APP_JWT_SECRET', 'development-only-change-me')
    jwt_algorithm: str = os.getenv('APP_JWT_ALGORITHM', 'HS256')
    jwt_issuer: str = os.getenv('APP_JWT_ISSUER', 'brawlerz-box-api')
    jwt_audience: str = os.getenv('APP_JWT_AUDIENCE', 'brawlerz-box-flutter')
    access_minutes: int = int(os.getenv('APP_ACCESS_TOKEN_MINUTES', '30'))
    refresh_days: int = int(os.getenv('APP_REFRESH_TOKEN_DAYS', '30'))
    cors_origins: list[str] = None  # type: ignore[assignment]
    seed_demo: bool = os.getenv('APP_SEED_DEMO', 'true').lower() in {'1', 'true', 'yes'}
    admin_email: str = os.getenv('APP_ADMIN_EMAIL', 'admin@brawlerzbox.com').lower()
    admin_password: str = os.getenv('APP_ADMIN_PASSWORD', 'ChangeMe123!')

    def __post_init__(self) -> None:
        object.__setattr__(self, 'cors_origins', _csv('CORS_ORIGINS', '*'))
        if self.env == 'production':
            if self.jwt_secret == 'development-only-change-me' or len(self.jwt_secret) < 32:
                raise RuntimeError('APP_JWT_SECRET must be a unique secret of at least 32 characters in production')
            if self.admin_password == 'ChangeMe123!':
                raise RuntimeError('APP_ADMIN_PASSWORD must be changed in production')


settings = Settings()
