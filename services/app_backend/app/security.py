from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import HTTPException, status

from .config import settings

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    try:
        return password_hasher.verify(encoded, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False


def create_token(*, user_id: int, role: str, token_type: str, lifetime: timedelta) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    expires = now + lifetime
    jti = secrets.token_urlsafe(24)
    payload: dict[str, Any] = {
        'sub': str(user_id),
        'role': role,
        'typ': token_type,
        'jti': jti,
        'iat': now,
        'nbf': now,
        'exp': expires,
        'iss': settings.jwt_issuer,
        'aud': settings.jwt_audience,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm), jti, expires


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token_expired') from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid_token') from exc
    if payload.get('typ') != expected_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong_token_type')
    return payload
