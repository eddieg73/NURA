from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main
from .db import get_db
from .models import ClinicalDraft, Encounter, OpsTask, User, utcnow
from .security import get_current_user


# Replace the broad organization export with an account-scoped export while
# retaining organization-scoped clinical review routes.
main.app.router.routes = [
    route
    for route in main.app.router.routes
    if not (
        getattr(route, "path", None) == f"{main.settings.api_prefix}/account/export"
        and "GET" in (getattr(route, "methods", set()) or set())
    )
]


@main.app.get(f"{main.settings.api_prefix}/account/export", tags=["account"])
def export_account_scoped(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    encounters = db.scalars(
        select(Encounter).where(
            Encounter.organization_id == user.organization_id,
            Encounter.created_by == user.id,
        )
    ).all()
    drafts = db.scalars(
        select(ClinicalDraft)
        .join(Encounter, ClinicalDraft.encounter_id == Encounter.id)
        .where(
            ClinicalDraft.organization_id == user.organization_id,
            Encounter.created_by == user.id,
        )
    ).all()
    tasks = db.scalars(
        select(OpsTask).where(
            OpsTask.organization_id == user.organization_id,
            OpsTask.user_id == user.id,
        )
    ).all()
    main.audit(
        db,
        action="account.export",
        actor=user,
        request_id=request.state.request_id,
    )
    db.commit()
    return {
        "exported_at": utcnow(),
        "user": main.user_out(user).model_dump(mode="json"),
        "encounters": [
            {
                "id": item.id,
                "patient_reference": item.patient_reference,
                "source_text": item.source_text,
                "consent_attested": item.consent_attested,
                "created_at": item.created_at,
            }
            for item in encounters
        ],
        "clinical_drafts": [
            main.draft_out(item).model_dump(mode="json") for item in drafts
        ],
        "tasks": [main.task_out(item).model_dump(mode="json") for item in tasks],
    }


app = main.app
