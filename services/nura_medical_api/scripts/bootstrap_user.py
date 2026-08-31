#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import AuditEvent, Organization, User
from app.security import hash_password


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an initial NURA Medical clinician, reviewer, or administrator."
    )
    parser.add_argument("--organization", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", required=True)
    parser.add_argument("--role", choices=["clinician", "reviewer", "admin"], required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    password = getpass.getpass("Password (12+ characters): ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters")

    Base.metadata.create_all(bind=engine)
    email = args.email.strip().lower()
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email)) is not None:
            raise SystemExit("A user with that email already exists")
        organization = db.scalar(
            select(Organization).where(Organization.name == args.organization.strip())
        )
        if organization is None:
            organization = Organization(name=args.organization.strip())
            db.add(organization)
            db.flush()
        user = User(
            organization_id=organization.id,
            email=email,
            full_name=args.full_name.strip(),
            password_hash=hash_password(password),
            role=args.role,
        )
        db.add(user)
        db.flush()
        db.add(
            AuditEvent(
                organization_id=organization.id,
                actor_id=user.id,
                action="account.bootstrap_created",
                entity_type="user",
                entity_id=user.id,
                metadata_json='{"source":"bootstrap_cli"}',
            )
        )
        db.commit()
        print(f"Created {args.role} {email} in {organization.name}")


if __name__ == "__main__":
    main()
