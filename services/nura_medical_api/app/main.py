from __future__ import annotations

import json
import secrets
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from .clinical import build_provider
from .config import get_settings
from .db import Base, SessionLocal, engine, get_db
from .models import (
    AuditEvent,
    ClinicalDraft,
    Encounter,
    OpsTask,
    Organization,
    RefreshSession,
    User,
    utcnow,
)
from .schemas import (
    AccountDeleteRequest,
    ClinicalDraftOut,
    ClinicalDraftRequest,
    LegalConfigOut,
    LoginRequest,
    LogoutRequest,
    ProvenanceItem,
    RefreshRequest,
    RegisterRequest,
    ReviewRequest,
    TaskCreate,
    TaskOut,
    TaskUpdate,
    TokenPair,
    UserOut,
)
from .security import (
    consume_refresh_session,
    create_access_token,
    create_refresh_session,
    get_current_user,
    hash_password,
    hash_refresh_token,
    require_roles,
    verify_password,
)


settings = get_settings()
provider = build_provider(settings)


def user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,  # type: ignore[arg-type]
        active=user.active,
    )


def task_out(task: OpsTask) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        detail=task.detail,
        status=task.status,
        priority=task.priority,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )


def draft_out(draft: ClinicalDraft) -> ClinicalDraftOut:
    return ClinicalDraftOut(
        id=draft.id,
        encounter_id=draft.encounter_id,
        operation=draft.operation,  # type: ignore[arg-type]
        output=json.loads(draft.output_json),
        provider_name=draft.provider_name,
        model_name=draft.model_name,
        status=draft.status,  # type: ignore[arg-type]
        created_at=draft.created_at,
        reviewed_by=draft.reviewed_by,
        reviewed_at=draft.reviewed_at,
        review_comment=draft.review_comment,
    )


def audit(
    db: Session,
    *,
    action: str,
    actor: User | None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    metadata: dict | None = None,
    request_id: str | None = None,
) -> None:
    db.add(
        AuditEvent(
            organization_id=actor.organization_id if actor else None,
            actor_id=actor.id if actor else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=json.dumps(metadata or {}, separators=(",", ":"), sort_keys=True),
            request_id=request_id,
        )
    )


def create_seed_user(
    db: Session,
    organization: Organization,
    email: str,
    password: str,
    role: str,
    full_name: str,
) -> None:
    normalized = email.strip().lower()
    if db.scalar(select(User).where(User.email == normalized)) is None:
        db.add(
            User(
                organization_id=organization.id,
                email=normalized,
                full_name=full_name,
                password_hash=hash_password(password),
                role=role,
            )
        )


def seed_demo(db: Session) -> None:
    if not settings.seed_demo_data:
        return
    organization = db.scalar(select(Organization).where(Organization.name == "NURA App Review"))
    if organization is None:
        organization = Organization(name="NURA App Review")
        db.add(organization)
        db.flush()
    create_seed_user(
        db,
        organization,
        settings.demo_clinician_email,
        settings.demo_clinician_password,
        "clinician",
        "App Review Clinician",
    )
    create_seed_user(
        db,
        organization,
        settings.demo_reviewer_email,
        settings.demo_reviewer_password,
        "reviewer",
        "App Review Reviewer",
    )
    create_seed_user(
        db,
        organization,
        settings.admin_email,
        settings.admin_password,
        "admin",
        "NURA Administrator",
    )
    db.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.validate_for_startup()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_demo(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Clinician-facing source capture, draft generation, review, and operations API. "
        "Clinical outputs are never final until an accountable clinician approves them."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)


@app.middleware("http")
async def request_controls(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or secrets.token_urlsafe(12)
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/healthz", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "nura-medical-api", "version": "1.0.0"}


@app.get("/readyz", tags=["system"])
def ready(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database_unavailable") from exc
    return {"status": "ready"}


@app.get(f"{settings.api_prefix}/legal", response_model=LegalConfigOut, tags=["account"])
def legal() -> LegalConfigOut:
    return LegalConfigOut(
        privacy_policy_url=settings.privacy_policy_url,
        terms_url=settings.terms_url,
        support_url=settings.support_url,
        clinical_disclaimer=(
            "NURA generates clinician decision-support drafts. It does not replace professional "
            "judgment, establish a diagnosis, or authorize treatment. Provider review is required."
        ),
    )


@app.post(f"{settings.api_prefix}/auth/register", response_model=TokenPair, tags=["auth"])
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    if not settings.allow_self_registration:
        raise HTTPException(status_code=403, detail="self_registration_disabled")
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status_code=409, detail="email_already_registered")
    organization = Organization(name=payload.organization_name.strip())
    db.add(organization)
    db.flush()
    user = User(
        organization_id=organization.id,
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role="clinician",
    )
    db.add(user)
    db.flush()
    access_token, expires_in = create_access_token(user, settings)
    refresh_token = create_refresh_session(db, user, settings, "registration")
    audit(db, action="auth.register", actor=user, request_id=request.state.request_id)
    db.commit()
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user=user_out(user),
    )


@app.post(f"{settings.api_prefix}/auth/login", response_model=TokenPair, tags=["auth"])
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash) or not user.active:
        raise HTTPException(status_code=401, detail="invalid_credentials")
    user.last_login_at = utcnow()
    access_token, expires_in = create_access_token(user, settings)
    refresh_token = create_refresh_session(db, user, settings, payload.device_label)
    audit(db, action="auth.login", actor=user, request_id=request.state.request_id)
    db.commit()
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user=user_out(user),
    )


@app.post(f"{settings.api_prefix}/auth/refresh", response_model=TokenPair, tags=["auth"])
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    old_session = consume_refresh_session(db, payload.refresh_token)
    user = db.get(User, old_session.user_id)
    if user is None or not user.active:
        raise HTTPException(status_code=401, detail="inactive_user")
    access_token, expires_in = create_access_token(user, settings)
    refresh_token = create_refresh_session(db, user, settings, payload.device_label)
    audit(db, action="auth.refresh", actor=user, request_id=request.state.request_id)
    db.commit()
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user=user_out(user),
    )


@app.post(f"{settings.api_prefix}/auth/logout", status_code=204, tags=["auth"])
def logout(payload: LogoutRequest, request: Request, db: Session = Depends(get_db)) -> Response:
    token_hash = hash_refresh_token(payload.refresh_token)
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash))
    if session is not None and session.revoked_at is None:
        session.revoked_at = utcnow()
        user = db.get(User, session.user_id)
        audit(db, action="auth.logout", actor=user, request_id=request.state.request_id)
        db.commit()
    return Response(status_code=204)


@app.get(f"{settings.api_prefix}/account/me", response_model=UserOut, tags=["account"])
def me(user: User = Depends(get_current_user)) -> UserOut:
    return user_out(user)


@app.get(f"{settings.api_prefix}/account/export", tags=["account"])
def export_account(
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
    audit(db, action="account.export", actor=user, request_id=request.state.request_id)
    db.commit()
    return {
        "exported_at": utcnow(),
        "user": user_out(user).model_dump(mode="json"),
        "encounters": [
            {
                "id": row.id,
                "patient_reference": row.patient_reference,
                "source_text": row.source_text,
                "consent_attested": row.consent_attested,
                "created_at": row.created_at,
            }
            for row in encounters
        ],
        "clinical_drafts": [draft_out(row).model_dump(mode="json") for row in drafts],
        "tasks": [task_out(row).model_dump(mode="json") for row in tasks],
    }


@app.delete(f"{settings.api_prefix}/account", status_code=204, tags=["account"])
def delete_account(
    payload: AccountDeleteRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid_credentials")
    organization_id = user.organization_id
    user_id = user.id
    db.execute(delete(RefreshSession).where(RefreshSession.user_id == user_id))
    db.delete(user)
    db.flush()
    db.add(
        AuditEvent(
            organization_id=organization_id,
            actor_id=None,
            action="account.deleted",
            entity_type="user",
            entity_id=None,
            metadata_json="{}",
            request_id=request.state.request_id,
        )
    )
    db.commit()
    return Response(status_code=204)


@app.post(
    f"{settings.api_prefix}/clinical/drafts",
    response_model=ClinicalDraftOut,
    tags=["clinical"],
)
async def create_clinical_draft(
    payload: ClinicalDraftRequest,
    request: Request,
    user: User = Depends(require_roles("clinician", "reviewer", "admin")),
    db: Session = Depends(get_db),
) -> ClinicalDraftOut:
    if not payload.consent_attested:
        raise HTTPException(status_code=422, detail="consent_attestation_required")
    if len(payload.case_text) > settings.max_case_characters:
        raise HTTPException(status_code=413, detail="case_text_too_large")

    encounter = Encounter(
        organization_id=user.organization_id,
        created_by=user.id,
        patient_reference=payload.patient_reference,
        source_text=payload.case_text,
        consent_attested=True,
    )
    db.add(encounter)
    db.flush()
    try:
        result = await provider.generate(payload.operation, payload.case_text, settings.evidence_as_of)
    except (httpx.HTTPError, RuntimeError, ValueError) as exc:
        audit(
            db,
            action="clinical.provider_failure",
            actor=user,
            entity_type="encounter",
            entity_id=encounter.id,
            metadata={"provider": settings.ai_provider, "error_type": type(exc).__name__},
            request_id=request.state.request_id,
        )
        db.commit()
        raise HTTPException(status_code=502, detail="clinical_provider_unavailable") from exc

    result.output.provenance.append(
        ProvenanceItem(
            source_type="encounter",
            source_id=encounter.id,
            note="User-entered source text",
        )
    )
    draft = ClinicalDraft(
        organization_id=user.organization_id,
        encounter_id=encounter.id,
        operation=payload.operation,
        output_json=result.output.model_dump_json(),
        provider_name=result.provider_name,
        model_name=result.model_name,
        status="draft",
    )
    db.add(draft)
    db.flush()
    audit(
        db,
        action="clinical.draft_created",
        actor=user,
        entity_type="clinical_draft",
        entity_id=draft.id,
        metadata={"operation": payload.operation, "provider": result.provider_name},
        request_id=request.state.request_id,
    )
    db.commit()
    return draft_out(draft)


@app.get(
    f"{settings.api_prefix}/clinical/drafts",
    response_model=list[ClinicalDraftOut],
    tags=["clinical"],
)
def list_clinical_drafts(
    user: User = Depends(require_roles("clinician", "reviewer", "admin")),
    db: Session = Depends(get_db),
) -> list[ClinicalDraftOut]:
    query = (
        select(ClinicalDraft)
        .where(ClinicalDraft.organization_id == user.organization_id)
        .order_by(ClinicalDraft.created_at.desc())
        .limit(100)
    )
    if user.role == "clinician":
        query = query.join(Encounter, ClinicalDraft.encounter_id == Encounter.id).where(
            Encounter.created_by == user.id
        )
    rows = db.scalars(query).all()
    return [draft_out(row) for row in rows]


@app.get(
    f"{settings.api_prefix}/clinical/drafts/{{draft_id}}",
    response_model=ClinicalDraftOut,
    tags=["clinical"],
)
def get_clinical_draft(
    draft_id: str,
    user: User = Depends(require_roles("clinician", "reviewer", "admin")),
    db: Session = Depends(get_db),
) -> ClinicalDraftOut:
    query = select(ClinicalDraft).where(
        ClinicalDraft.id == draft_id,
        ClinicalDraft.organization_id == user.organization_id,
    )
    if user.role == "clinician":
        query = query.join(Encounter, ClinicalDraft.encounter_id == Encounter.id).where(
            Encounter.created_by == user.id
        )
    draft = db.scalar(query)
    if draft is None:
        raise HTTPException(status_code=404, detail="draft_not_found")
    return draft_out(draft)


@app.post(
    f"{settings.api_prefix}/clinical/drafts/{{draft_id}}/review",
    response_model=ClinicalDraftOut,
    tags=["clinical"],
)
def review_clinical_draft(
    draft_id: str,
    payload: ReviewRequest,
    request: Request,
    user: User = Depends(require_roles("reviewer", "admin")),
    db: Session = Depends(get_db),
) -> ClinicalDraftOut:
    draft = db.scalar(
        select(ClinicalDraft).where(
            ClinicalDraft.id == draft_id,
            ClinicalDraft.organization_id == user.organization_id,
        )
    )
    if draft is None:
        raise HTTPException(status_code=404, detail="draft_not_found")
    draft.status = payload.status
    draft.reviewed_by = user.id
    draft.reviewed_at = utcnow()
    draft.review_comment = payload.comment
    audit(
        db,
        action=f"clinical.draft_{payload.status}",
        actor=user,
        entity_type="clinical_draft",
        entity_id=draft.id,
        request_id=request.state.request_id,
    )
    db.commit()
    return draft_out(draft)


@app.get(f"{settings.api_prefix}/ops/tasks", response_model=list[TaskOut], tags=["operations"])
def list_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TaskOut]:
    rows = db.scalars(
        select(OpsTask)
        .where(OpsTask.user_id == user.id, OpsTask.organization_id == user.organization_id)
        .order_by(OpsTask.created_at.desc())
        .limit(200)
    ).all()
    return [task_out(row) for row in rows]


@app.post(f"{settings.api_prefix}/ops/tasks", response_model=TaskOut, tags=["operations"])
def create_task(
    payload: TaskCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskOut:
    task = OpsTask(
        organization_id=user.organization_id,
        user_id=user.id,
        title=payload.title.strip(),
        detail=payload.detail,
        priority=payload.priority,
    )
    db.add(task)
    db.flush()
    audit(
        db,
        action="ops.task_created",
        actor=user,
        entity_type="ops_task",
        entity_id=task.id,
        request_id=request.state.request_id,
    )
    db.commit()
    return task_out(task)


@app.patch(
    f"{settings.api_prefix}/ops/tasks/{{task_id}}",
    response_model=TaskOut,
    tags=["operations"],
)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskOut:
    task = db.scalar(
        select(OpsTask).where(
            OpsTask.id == task_id,
            OpsTask.user_id == user.id,
            OpsTask.organization_id == user.organization_id,
        )
    )
    if task is None:
        raise HTTPException(status_code=404, detail="task_not_found")
    changes = payload.model_dump(exclude_none=True)
    for field, value in changes.items():
        setattr(task, field, value)
    if payload.status == "completed":
        task.completed_at = utcnow()
    elif payload.status is not None:
        task.completed_at = None
    audit(
        db,
        action="ops.task_updated",
        actor=user,
        entity_type="ops_task",
        entity_id=task.id,
        metadata={"fields": sorted(changes.keys())},
        request_id=request.state.request_id,
    )
    db.commit()
    return task_out(task)


@app.get(f"{settings.api_prefix}/admin/audit", tags=["administration"])
def audit_events(
    user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = db.scalars(
        select(AuditEvent)
        .where(AuditEvent.organization_id == user.organization_id)
        .order_by(AuditEvent.created_at.desc())
        .limit(250)
    ).all()
    return [
        {
            "id": row.id,
            "actor_id": row.actor_id,
            "action": row.action,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "metadata": json.loads(row.metadata_json),
            "request_id": row.request_id,
            "created_at": row.created_at,
        }
        for row in rows
    ]
