from __future__ import annotations

import json
import secrets
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .db import (
    CartItem,
    CheckIn,
    ClassReservation,
    ClassSession,
    IntegrationConnection,
    Meal,
    NutritionProfile,
    Order,
    OrderItem,
    ProgressPoint,
    QRPass,
    RefreshSession,
    SessionLocal,
    Supplement,
    User,
    UserMetric,
    Workout,
    init_db,
    utcnow,
)
from .security import create_token, decode_token, hash_password, verify_password


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    displayName: str = Field(min_length=1, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refreshToken: str


class TokenOut(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = 'bearer'
    expiresIn: int


class NutritionUpdate(BaseModel):
    dailyCalories: int | None = Field(default=None, ge=0)
    targetCalories: int | None = Field(default=None, gt=0)
    proteinGrams: float | None = Field(default=None, ge=0)
    proteinTarget: float | None = Field(default=None, gt=0)
    carbsGrams: float | None = Field(default=None, ge=0)
    carbsTarget: float | None = Field(default=None, gt=0)
    fatGrams: float | None = Field(default=None, ge=0)
    fatTarget: float | None = Field(default=None, gt=0)


class MetricUpdate(BaseModel):
    readinessScore: int | None = Field(default=None, ge=0, le=100)
    hrv: int | None = Field(default=None, ge=0, le=500)
    sleepScore: int | None = Field(default=None, ge=0, le=100)
    recoveryPercentage: int | None = Field(default=None, ge=0, le=100)


class MealIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    calories: int = Field(ge=0, le=10000)
    time: str = Field(min_length=1, max_length=32)
    imageUrl: str = Field(default='', max_length=2048)


class ProgressIn(BaseModel):
    kind: Literal['strength', 'weight']
    x: float
    y: float


class IntegrationIn(BaseModel):
    connected: bool


class QRPassIn(BaseModel):
    ttlMinutes: int = Field(default=10, ge=1, le=60)


class QRValidateIn(BaseModel):
    token: str = Field(min_length=20, max_length=128)


class CartIn(BaseModel):
    quantity: int = Field(ge=0, le=99)


class ClassWrite(BaseModel):
    id: str | None = Field(default=None, max_length=64)
    name: str = Field(min_length=1, max_length=160)
    startTime: datetime
    trainer: str = Field(min_length=1, max_length=120)
    durationMinutes: int = Field(gt=0, le=360)
    capacity: int = Field(default=25, gt=0, le=500)


class WorkoutWrite(BaseModel):
    id: str | None = Field(default=None, max_length=64)
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(min_length=1, max_length=5000)
    level: str = Field(min_length=1, max_length=64)
    duration: str = Field(min_length=1, max_length=64)
    imageUrl: str = Field(default='', max_length=2048)
    category: str = Field(min_length=1, max_length=64)


class SupplementWrite(BaseModel):
    id: str | None = Field(default=None, max_length=64)
    name: str = Field(min_length=1, max_length=180)
    description: str = Field(min_length=1, max_length=5000)
    price: float = Field(ge=0, le=100000)
    imageUrl: str = Field(default='', max_length=2048)
    tags: list[str] = Field(default_factory=list, max_length=20)
    inventory: int = Field(default=0, ge=0)


class AIAnalyzeIn(BaseModel):
    exercise: str = Field(min_length=1, max_length=120)
    observations: list[str] = Field(default_factory=list, max_length=50)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Db = Annotated[Session, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


def current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Db) -> User:
    payload = decode_token(token, 'access')
    try:
        user_id = int(payload['sub'])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail='invalid_subject') from exc
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail='inactive_or_missing_user')
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def admin_user(user: CurrentUser) -> User:
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='admin_required')
    return user


AdminUser = Annotated[User, Depends(admin_user)]


def ensure_member_defaults(db: Session, user_id: int) -> None:
    if db.get(UserMetric, user_id) is None:
        db.add(UserMetric(user_id=user_id))
    if db.get(NutritionProfile, user_id) is None:
        db.add(NutritionProfile(user_id=user_id))
    if db.scalar(select(Meal.id).where(Meal.user_id == user_id).limit(1)) is None:
        db.add_all([
            Meal(user_id=user_id, name='Protein Oatmeal', calories=450, time='08:00 AM', image_url='https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=500'),
            Meal(user_id=user_id, name='Chicken Breast & Quinoa', calories=650, time='01:30 PM', image_url='https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=500'),
            Meal(user_id=user_id, name='Post-Workout Shake', calories=250, time='05:00 PM', image_url='https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=500'),
        ])
    if db.scalar(select(ProgressPoint.id).where(ProgressPoint.user_id == user_id).limit(1)) is None:
        db.add_all([ProgressPoint(user_id=user_id, kind='strength', x=float(i), y=float(y)) for i, y in enumerate([100, 105, 103, 110, 115, 120, 125])])
        db.add_all([ProgressPoint(user_id=user_id, kind='weight', x=float(i), y=float(y)) for i, y in enumerate([85, 84.5, 84.2, 83.8, 83.5, 83, 82.5])])
    for provider in ('apple_health', 'whoop', 'garmin', 'google_fit'):
        if db.get(IntegrationConnection, {'user_id': user_id, 'provider': provider}) is None:
            db.add(IntegrationConnection(user_id=user_id, provider=provider, connected=False))
    db.commit()


def seed_catalog(db: Session) -> None:
    if db.scalar(select(ClassSession.id).limit(1)) is None:
        now = datetime.now(timezone.utc)
        db.add_all([
            ClassSession(id='1', name='Boxing Fundamentals', trainer='Coach Mike', start_time=now + timedelta(days=1, hours=2), duration_minutes=60, capacity=25),
            ClassSession(id='2', name='HIIT Training', trainer='Coach Sarah', start_time=now + timedelta(days=2), duration_minutes=45, capacity=20),
            ClassSession(id='3', name='MMA Conditioning', trainer='Coach Alex', start_time=now + timedelta(days=3), duration_minutes=90, capacity=15),
            ClassSession(id='4', name='Personal Training', trainer='Coach Elena', start_time=now + timedelta(days=4), duration_minutes=60, capacity=8),
        ])
    if db.scalar(select(Workout.id).limit(1)) is None:
        db.add_all([
            Workout(id='1', title='Boxing Fundamentals', description='Master the basics of boxing footwork and punches.', level='Beginner', duration='45 min', category='Boxing', image_url='https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=500'),
            Workout(id='2', title='Heavy Bag Power', description='High intensity drills to build explosive power.', level='Intermediate', duration='30 min', category='Boxing', image_url='https://images.unsplash.com/photo-1517438322351-db62136e01a0?w=500'),
            Workout(id='3', title='Full Body Strength', description='Compound lifts and functional movements.', level='Beginner', duration='60 min', category='Strength', image_url='https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500'),
            Workout(id='4', title='HIIT Conditioning', description='Fast-paced circuits to burn fat and increase stamina.', level='Advanced', duration='25 min', category='HIIT', image_url='https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500'),
        ])
    if db.scalar(select(Supplement.id).limit(1)) is None:
        db.add_all([
            Supplement(id='1', name='Whey Protein Isolate', description='Premium whey isolate for post-workout nutrition.', price_cents=5499, image_url='https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=500', tags_json=json.dumps(['Third Party Tested', 'GMP Certified']), inventory=50),
            Supplement(id='2', name='Creatine Monohydrate', description='Creatine monohydrate for performance support.', price_cents=2999, image_url='https://images.unsplash.com/photo-1549477228-8d515d39c4ef?w=500', tags_json=json.dumps(['Third Party Tested', 'GMP Certified']), inventory=75),
            Supplement(id='3', name='Sleep Restore', description='Magnesium-based nighttime recovery supplement.', price_cents=3499, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500', tags_json=json.dumps(['Third Party Tested', 'GMP Certified']), inventory=30),
            Supplement(id='4', name='Omega-3 Fish Oil', description='EPA/DHA dietary supplement.', price_cents=2499, image_url='https://images.unsplash.com/photo-1576073719710-aa6e651b77bd?w=500', tags_json=json.dumps(['Third Party Tested']), inventory=45),
        ])
    db.commit()


def seed_users(db: Session) -> None:
    admin = db.scalar(select(User).where(User.email == settings.admin_email))
    if admin is None:
        admin = User(email=settings.admin_email, display_name='Administrator', password_hash=hash_password(settings.admin_password), role='admin')
        db.add(admin)
        db.commit()
        db.refresh(admin)
    ensure_member_defaults(db, admin.id)
    if settings.seed_demo:
        demo = db.scalar(select(User).where(User.email == 'demo@brawlerzbox.com'))
        if demo is None:
            demo = User(email='demo@brawlerzbox.com', display_name='Jessica', password_hash=hash_password('DemoPass123!'), role='member')
            db.add(demo)
            db.commit()
            db.refresh(demo)
        ensure_member_defaults(db, demo.id)


def issue_tokens(db: Session, user: User) -> TokenOut:
    access, _, _ = create_token(user_id=user.id, role=user.role, token_type='access', lifetime=timedelta(minutes=settings.access_minutes))
    refresh, refresh_jti, refresh_exp = create_token(user_id=user.id, role=user.role, token_type='refresh', lifetime=timedelta(days=settings.refresh_days))
    db.add(RefreshSession(jti=refresh_jti, user_id=user.id, expires_at=refresh_exp))
    db.commit()
    return TokenOut(accessToken=access, refreshToken=refresh, expiresIn=settings.access_minutes * 60)


def user_json(user: User) -> dict[str, Any]:
    return {'id': user.id, 'email': user.email, 'displayName': user.display_name, 'role': user.role, 'createdAt': user.created_at}


def class_json(db: Session, row: ClassSession, user_id: int) -> dict[str, Any]:
    reserved_count = db.scalar(select(func.count(ClassReservation.id)).where(ClassReservation.class_id == row.id)) or 0
    is_reserved = db.scalar(select(ClassReservation.id).where(ClassReservation.class_id == row.id, ClassReservation.user_id == user_id).limit(1)) is not None
    return {'id': row.id, 'name': row.name, 'startTime': row.start_time, 'trainer': row.trainer, 'durationMinutes': row.duration_minutes, 'capacity': row.capacity, 'reservedCount': reserved_count, 'isReserved': is_reserved}


def supplement_json(row: Supplement) -> dict[str, Any]:
    return {'id': row.id, 'name': row.name, 'description': row.description, 'price': row.price_cents / 100, 'imageUrl': row.image_url, 'tags': row.tags, 'inventory': row.inventory, 'inStock': row.inventory > 0}


def nutrition_json(db: Session, user_id: int) -> dict[str, Any]:
    profile = db.get(NutritionProfile, user_id)
    if profile is None:
        ensure_member_defaults(db, user_id)
        profile = db.get(NutritionProfile, user_id)
    meals = db.scalars(select(Meal).where(Meal.user_id == user_id).order_by(Meal.id)).all()
    return {
        'dailyCalories': profile.daily_calories,
        'targetCalories': profile.target_calories,
        'proteinGrams': profile.protein_grams,
        'proteinTarget': profile.protein_target,
        'carbsGrams': profile.carbs_grams,
        'carbsTarget': profile.carbs_target,
        'fatGrams': profile.fat_grams,
        'fatTarget': profile.fat_target,
        'meals': [{'id': row.id, 'name': row.name, 'calories': row.calories, 'time': row.time, 'imageUrl': row.image_url} for row in meals],
    }


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_catalog(db)
        seed_users(db)
    yield


app = FastAPI(title='Brawlerz Box / NURA Flutter Backend', version='1.0.0', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allow_headers=['Authorization', 'Content-Type', 'X-Request-ID'],
)


@app.middleware('http')
async def request_context(request: Request, call_next):
    request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
    response: Response = await call_next(request)
    response.headers['X-Request-ID'] = request_id
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


@app.get('/healthz')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': 'nura-flutter-backend', 'version': '1.0.0'}


@app.get('/readyz')
def ready(db: Db) -> dict[str, str]:
    db.execute(text('SELECT 1'))
    return {'status': 'ready'}


@app.post('/api/v1/auth/register', response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, db: Db):
    email = str(payload.email).strip().lower()
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(status_code=409, detail='email_already_registered')
    user = User(email=email, display_name=payload.displayName.strip(), password_hash=hash_password(payload.password), role='member')
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail='email_already_registered') from exc
    db.refresh(user)
    ensure_member_defaults(db, user.id)
    return issue_tokens(db, user)


@app.post('/api/v1/auth/login', response_model=TokenOut)
def login(payload: LoginIn, db: Db):
    user = db.scalar(select(User).where(User.email == str(payload.email).strip().lower()))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='invalid_credentials')
    return issue_tokens(db, user)


@app.post('/api/v1/auth/refresh', response_model=TokenOut)
def refresh(payload: RefreshIn, db: Db):
    claims = decode_token(payload.refreshToken, 'refresh')
    jti = str(claims.get('jti', ''))
    session = db.get(RefreshSession, jti)
    if session is None or session.revoked_at is not None or as_utc(session.expires_at) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail='refresh_session_invalid')
    user = db.get(User, int(claims['sub']))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail='inactive_or_missing_user')
    session.revoked_at = utcnow()
    db.commit()
    return issue_tokens(db, user)


@app.post('/api/v1/auth/logout', status_code=204)
def logout(payload: RefreshIn, db: Db):
    try:
        claims = decode_token(payload.refreshToken, 'refresh')
        session = db.get(RefreshSession, str(claims.get('jti', '')))
        if session is not None and session.revoked_at is None:
            session.revoked_at = utcnow()
            db.commit()
    except HTTPException:
        pass
    return Response(status_code=204)


@app.get('/api/v1/auth/me')
def me(user: CurrentUser):
    return user_json(user)


@app.get('/api/v1/dashboard')
def dashboard(user: CurrentUser, db: Db):
    metric = db.get(UserMetric, user.id)
    if metric is None:
        ensure_member_defaults(db, user.id)
        metric = db.get(UserMetric, user.id)
    next_workout = db.scalar(select(Workout).where(Workout.active.is_(True)).order_by(Workout.id).limit(1))
    return {
        'user': user_json(user),
        'readinessScore': metric.readiness_score,
        'hrv': metric.hrv,
        'sleepScore': metric.sleep_score,
        'recoveryPercentage': metric.recovery_percentage,
        'reservedClasses': db.scalar(select(func.count(ClassReservation.id)).where(ClassReservation.user_id == user.id)) or 0,
        'activeIntegrations': db.scalar(select(func.count(IntegrationConnection.provider)).where(IntegrationConnection.user_id == user.id, IntegrationConnection.connected.is_(True))) or 0,
        'todayWorkout': None if next_workout is None else {'id': next_workout.id, 'title': next_workout.title, 'description': next_workout.description, 'level': next_workout.level, 'duration': next_workout.duration, 'imageUrl': next_workout.image_url, 'category': next_workout.category},
    }


@app.get('/api/v1/metrics')
def get_metrics(user: CurrentUser, db: Db):
    metric = db.get(UserMetric, user.id)
    if metric is None:
        ensure_member_defaults(db, user.id)
        metric = db.get(UserMetric, user.id)
    strength = db.scalars(select(ProgressPoint).where(ProgressPoint.user_id == user.id, ProgressPoint.kind == 'strength').order_by(ProgressPoint.x)).all()
    weight = db.scalars(select(ProgressPoint).where(ProgressPoint.user_id == user.id, ProgressPoint.kind == 'weight').order_by(ProgressPoint.x)).all()
    return {'readinessScore': metric.readiness_score, 'hrv': metric.hrv, 'sleepScore': metric.sleep_score, 'recoveryPercentage': metric.recovery_percentage, 'strengthHistory': [{'x': p.x, 'y': p.y} for p in strength], 'weightHistory': [{'x': p.x, 'y': p.y} for p in weight], 'updatedAt': metric.updated_at}


@app.put('/api/v1/metrics')
def update_metrics(payload: MetricUpdate, user: CurrentUser, db: Db):
    metric = db.get(UserMetric, user.id) or UserMetric(user_id=user.id)
    mapping = {'readinessScore': 'readiness_score', 'hrv': 'hrv', 'sleepScore': 'sleep_score', 'recoveryPercentage': 'recovery_percentage'}
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(metric, mapping[key], value)
    metric.updated_at = utcnow()
    db.add(metric)
    db.commit()
    return get_metrics(user, db)


@app.post('/api/v1/progress', status_code=201)
def add_progress(payload: ProgressIn, user: CurrentUser, db: Db):
    point = ProgressPoint(user_id=user.id, kind=payload.kind, x=payload.x, y=payload.y)
    db.add(point)
    db.commit()
    db.refresh(point)
    return {'id': point.id, 'kind': point.kind, 'x': point.x, 'y': point.y, 'recordedAt': point.recorded_at}


@app.get('/api/v1/classes')
def list_classes(user: CurrentUser, db: Db):
    rows = db.scalars(select(ClassSession).where(ClassSession.active.is_(True)).order_by(ClassSession.start_time)).all()
    return [class_json(db, row, user.id) for row in rows]


@app.post('/api/v1/classes/{class_id}/reserve')
def reserve_class(class_id: str, user: CurrentUser, db: Db):
    row = db.get(ClassSession, class_id)
    if row is None or not row.active:
        raise HTTPException(status_code=404, detail='class_not_found')
    existing = db.scalar(select(ClassReservation).where(ClassReservation.class_id == class_id, ClassReservation.user_id == user.id))
    if existing is None:
        reserved_count = db.scalar(select(func.count(ClassReservation.id)).where(ClassReservation.class_id == class_id)) or 0
        if reserved_count >= row.capacity:
            raise HTTPException(status_code=409, detail='class_full')
        db.add(ClassReservation(class_id=class_id, user_id=user.id))
        db.commit()
    return class_json(db, row, user.id)


@app.delete('/api/v1/classes/{class_id}/reserve')
def cancel_reservation(class_id: str, user: CurrentUser, db: Db):
    row = db.get(ClassSession, class_id)
    if row is None:
        raise HTTPException(status_code=404, detail='class_not_found')
    db.execute(delete(ClassReservation).where(ClassReservation.class_id == class_id, ClassReservation.user_id == user.id))
    db.commit()
    return class_json(db, row, user.id)


@app.get('/api/v1/workouts')
def list_workouts(_: CurrentUser, db: Db, category: str | None = Query(default=None, max_length=64)):
    query = select(Workout).where(Workout.active.is_(True))
    if category:
        query = query.where(func.lower(Workout.category) == category.lower())
    rows = db.scalars(query.order_by(Workout.id)).all()
    return [{'id': row.id, 'title': row.title, 'description': row.description, 'level': row.level, 'duration': row.duration, 'imageUrl': row.image_url, 'category': row.category} for row in rows]


@app.get('/api/v1/supplements')
def list_supplements(_: CurrentUser, db: Db):
    rows = db.scalars(select(Supplement).where(Supplement.active.is_(True)).order_by(Supplement.id)).all()
    return [supplement_json(row) for row in rows]


@app.get('/api/v1/nutrition')
def get_nutrition(user: CurrentUser, db: Db):
    return nutrition_json(db, user.id)


@app.put('/api/v1/nutrition')
def update_nutrition(payload: NutritionUpdate, user: CurrentUser, db: Db):
    profile = db.get(NutritionProfile, user.id) or NutritionProfile(user_id=user.id)
    mapping = {'dailyCalories': 'daily_calories', 'targetCalories': 'target_calories', 'proteinGrams': 'protein_grams', 'proteinTarget': 'protein_target', 'carbsGrams': 'carbs_grams', 'carbsTarget': 'carbs_target', 'fatGrams': 'fat_grams', 'fatTarget': 'fat_target'}
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(profile, mapping[key], value)
    db.add(profile)
    db.commit()
    return nutrition_json(db, user.id)


@app.post('/api/v1/nutrition/meals', status_code=201)
def add_meal(payload: MealIn, user: CurrentUser, db: Db):
    row = Meal(user_id=user.id, name=payload.name, calories=payload.calories, time=payload.time, image_url=payload.imageUrl)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {'id': row.id, 'name': row.name, 'calories': row.calories, 'time': row.time, 'imageUrl': row.image_url}


@app.delete('/api/v1/nutrition/meals/{meal_id}', status_code=204)
def delete_meal(meal_id: int, user: CurrentUser, db: Db):
    row = db.scalar(select(Meal).where(Meal.id == meal_id, Meal.user_id == user.id))
    if row is None:
        raise HTTPException(status_code=404, detail='meal_not_found')
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@app.get('/api/v1/integrations')
def list_integrations(user: CurrentUser, db: Db):
    rows = db.scalars(select(IntegrationConnection).where(IntegrationConnection.user_id == user.id).order_by(IntegrationConnection.provider)).all()
    return [{'provider': row.provider, 'connected': row.connected, 'updatedAt': row.updated_at} for row in rows]


@app.put('/api/v1/integrations/{provider}')
def update_integration(provider: str, payload: IntegrationIn, user: CurrentUser, db: Db):
    provider = provider.strip().lower()
    if provider not in {'apple_health', 'whoop', 'garmin', 'google_fit'}:
        raise HTTPException(status_code=400, detail='unsupported_provider')
    row = db.get(IntegrationConnection, {'user_id': user.id, 'provider': provider}) or IntegrationConnection(user_id=user.id, provider=provider)
    row.connected = payload.connected
    row.updated_at = utcnow()
    db.add(row)
    db.commit()
    return {'provider': row.provider, 'connected': row.connected, 'updatedAt': row.updated_at}


@app.post('/api/v1/qr/pass', status_code=201)
def create_qr_pass(payload: QRPassIn, user: CurrentUser, db: Db):
    now = datetime.now(timezone.utc)
    db.execute(delete(QRPass).where(QRPass.user_id == user.id, QRPass.expires_at < now))
    token = secrets.token_urlsafe(32)
    expires = now + timedelta(minutes=payload.ttlMinutes)
    db.add(QRPass(token=token, user_id=user.id, expires_at=expires))
    db.commit()
    return {'token': token, 'memberId': str(user.id), 'expiresAt': expires}


@app.get('/api/v1/qr/history')
def qr_history(user: CurrentUser, db: Db):
    rows = db.scalars(select(CheckIn).where(CheckIn.user_id == user.id).order_by(CheckIn.checked_in_at.desc()).limit(20)).all()
    return [{'id': row.id, 'checkedInAt': row.checked_in_at} for row in rows]


@app.post('/api/v1/qr/validate')
def validate_qr(payload: QRValidateIn, _: AdminUser, db: Db):
    row = db.get(QRPass, payload.token)
    now = datetime.now(timezone.utc)
    valid = row is not None and row.revoked_at is None and as_utc(row.expires_at) > now
    if not valid:
        return {'valid': False, 'memberId': None, 'checkedInAt': None}
    existing = db.scalar(select(CheckIn).where(CheckIn.qr_token == row.token))
    if existing is None:
        existing = CheckIn(user_id=row.user_id, qr_token=row.token)
        db.add(existing)
        row.revoked_at = utcnow()
        db.commit()
        db.refresh(existing)
    return {'valid': True, 'memberId': str(row.user_id), 'checkedInAt': existing.checked_in_at}


@app.get('/api/v1/cart')
def get_cart(user: CurrentUser, db: Db):
    rows = db.execute(select(CartItem, Supplement).join(Supplement, Supplement.id == CartItem.supplement_id).where(CartItem.user_id == user.id)).all()
    items = [{'supplement': supplement_json(product), 'quantity': item.quantity, 'lineTotal': item.quantity * product.price_cents / 100} for item, product in rows]
    return {'items': items, 'total': sum(item['lineTotal'] for item in items)}


@app.put('/api/v1/cart/{supplement_id}')
def set_cart_item(supplement_id: str, payload: CartIn, user: CurrentUser, db: Db):
    product = db.get(Supplement, supplement_id)
    if product is None or not product.active:
        raise HTTPException(status_code=404, detail='supplement_not_found')
    row = db.get(CartItem, {'user_id': user.id, 'supplement_id': supplement_id})
    if payload.quantity == 0:
        if row is not None:
            db.delete(row)
    else:
        if payload.quantity > product.inventory:
            raise HTTPException(status_code=409, detail='insufficient_inventory')
        if row is None:
            row = CartItem(user_id=user.id, supplement_id=supplement_id, quantity=payload.quantity)
            db.add(row)
        else:
            row.quantity = payload.quantity
    db.commit()
    return get_cart(user, db)


@app.post('/api/v1/orders', status_code=201)
def create_order(user: CurrentUser, db: Db, idempotency_key: Annotated[str | None, Header(alias='Idempotency-Key')] = None):
    rows = db.execute(select(CartItem, Supplement).join(Supplement, Supplement.id == CartItem.supplement_id).where(CartItem.user_id == user.id)).all()
    if not rows:
        raise HTTPException(status_code=409, detail='cart_empty')
    for item, product in rows:
        if item.quantity > product.inventory:
            raise HTTPException(status_code=409, detail=f'insufficient_inventory:{product.id}')
    total = sum(item.quantity * product.price_cents for item, product in rows)
    order = Order(user_id=user.id, total_cents=total, status='pending')
    db.add(order)
    db.flush()
    for item, product in rows:
        db.add(OrderItem(order_id=order.id, supplement_id=product.id, name_snapshot=product.name, quantity=item.quantity, unit_price_cents=product.price_cents))
        product.inventory -= item.quantity
        db.delete(item)
    db.commit()
    db.refresh(order)
    return {'id': order.id, 'status': order.status, 'total': order.total_cents / 100, 'createdAt': order.created_at, 'idempotencyKey': idempotency_key}


@app.get('/api/v1/orders')
def list_orders(user: CurrentUser, db: Db):
    rows = db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())).all()
    return [{'id': row.id, 'status': row.status, 'total': row.total_cents / 100, 'createdAt': row.created_at} for row in rows]


@app.post('/api/v1/ai-coach/analyze')
def ai_coach_analyze(payload: AIAnalyzeIn, _: CurrentUser):
    return {
        'status': 'received',
        'exercise': payload.exercise,
        'observations': payload.observations,
        'feedback': ['Model integration is not enabled. No computer-vision or clinical inference was performed.'],
        'confidence': None,
        'requiresHumanReview': True,
    }


@app.get('/api/v1/admin/summary')
def admin_summary(_: AdminUser, db: Db):
    today = datetime.now(timezone.utc).date()
    checkins_today = db.scalar(select(func.count(CheckIn.id)).where(func.date(CheckIn.checked_in_at) == today.isoformat())) or 0
    revenue_cents = db.scalar(select(func.coalesce(func.sum(Order.total_cents), 0))) or 0
    top_rows = db.execute(select(ClassSession, func.count(ClassReservation.id).label('reserved')).outerjoin(ClassReservation, ClassReservation.class_id == ClassSession.id).group_by(ClassSession.id).order_by(func.count(ClassReservation.id).desc()).limit(5)).all()
    return {
        'totalMembers': db.scalar(select(func.count(User.id)).where(User.role == 'member', User.is_active.is_(True))) or 0,
        'checkInsToday': checkins_today,
        'revenue': revenue_cents / 100,
        'activeSubscriptionsPercent': 100,
        'topClasses': [{'id': row.id, 'name': row.name, 'time': row.start_time, 'attendance': reserved, 'capacity': row.capacity} for row, reserved in top_rows],
    }


@app.post('/api/v1/admin/classes', status_code=201)
def admin_create_class(payload: ClassWrite, _: AdminUser, db: Db):
    row = ClassSession(id=payload.id or uuid.uuid4().hex, name=payload.name, start_time=payload.startTime, trainer=payload.trainer, duration_minutes=payload.durationMinutes, capacity=payload.capacity)
    db.add(row)
    db.commit()
    return class_json(db, row, 0)


@app.post('/api/v1/admin/workouts', status_code=201)
def admin_create_workout(payload: WorkoutWrite, _: AdminUser, db: Db):
    row = Workout(id=payload.id or uuid.uuid4().hex, title=payload.title, description=payload.description, level=payload.level, duration=payload.duration, image_url=payload.imageUrl, category=payload.category)
    db.add(row)
    db.commit()
    return {'id': row.id, 'title': row.title, 'description': row.description, 'level': row.level, 'duration': row.duration, 'imageUrl': row.image_url, 'category': row.category}


@app.post('/api/v1/admin/supplements', status_code=201)
def admin_create_supplement(payload: SupplementWrite, _: AdminUser, db: Db):
    row = Supplement(id=payload.id or uuid.uuid4().hex, name=payload.name, description=payload.description, price_cents=round(payload.price * 100), image_url=payload.imageUrl, tags_json=json.dumps(payload.tags), inventory=payload.inventory)
    db.add(row)
    db.commit()
    return supplement_json(row)
