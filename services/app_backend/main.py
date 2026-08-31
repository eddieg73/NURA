import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nura_app.db")
API_TOKEN = os.getenv("APP_API_TOKEN", "dev-change-me")
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class ClassSessionDB(Base):
    __tablename__ = "class_sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    trainer: Mapped[str] = mapped_column(String)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    is_reserved: Mapped[bool] = mapped_column(Boolean, default=False)

class WorkoutDB(Base):
    __tablename__ = "workouts"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    level: Mapped[str] = mapped_column(String)
    duration: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String, default="")
    category: Mapped[str] = mapped_column(String)

class SupplementDB(Base):
    __tablename__ = "supplements"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    image_url: Mapped[str] = mapped_column(String, default="")
    category: Mapped[str] = mapped_column(String, default="General")

class MetricDB(Base):
    __tablename__ = "user_metrics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    readiness_score: Mapped[int] = mapped_column(Integer, default=88)
    hrv: Mapped[int] = mapped_column(Integer, default=65)
    sleep_score: Mapped[int] = mapped_column(Integer, default=82)
    recovery_percentage: Mapped[int] = mapped_column(Integer, default=75)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class NutritionDB(Base):
    __tablename__ = "nutrition"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    daily_calories: Mapped[int] = mapped_column(Integer, default=1850)
    target_calories: Mapped[int] = mapped_column(Integer, default=2400)
    protein_grams: Mapped[float] = mapped_column(Float, default=145)
    protein_target: Mapped[float] = mapped_column(Float, default=180)
    carbs_grams: Mapped[float] = mapped_column(Float, default=190)
    carbs_target: Mapped[float] = mapped_column(Float, default=260)
    fat_grams: Mapped[float] = mapped_column(Float, default=58)
    fat_target: Mapped[float] = mapped_column(Float, default=75)

class MealDB(Base):
    __tablename__ = "meals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    calories: Mapped[int] = mapped_column(Integer)
    time: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String, default="")

class ProgressDB(Base):
    __tablename__ = "progress_points"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String)  # strength | weight
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)

class IntegrationDB(Base):
    __tablename__ = "integrations"
    provider: Mapped[str] = mapped_column(String, primary_key=True)
    connected: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class QRPassDB(Base):
    __tablename__ = "qr_passes"
    token: Mapped[str] = mapped_column(String, primary_key=True)
    member_id: Mapped[str] = mapped_column(String)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

Base.metadata.create_all(engine)

class ClassOut(BaseModel):
    id: str
    name: str
    startTime: datetime
    trainer: str
    durationMinutes: int
    isReserved: bool

class ReservationOut(BaseModel):
    id: str
    isReserved: bool

class NutritionUpdate(BaseModel):
    dailyCalories: Optional[int] = None
    targetCalories: Optional[int] = None
    proteinGrams: Optional[float] = None
    proteinTarget: Optional[float] = None
    carbsGrams: Optional[float] = None
    carbsTarget: Optional[float] = None
    fatGrams: Optional[float] = None
    fatTarget: Optional[float] = None

class MealIn(BaseModel):
    name: str
    calories: int = Field(ge=0)
    time: str
    imageUrl: str = ""

class IntegrationIn(BaseModel):
    connected: bool

class QRValidateIn(BaseModel):
    token: str

class QRCreateIn(BaseModel):
    memberId: str = "demo-member"
    ttlMinutes: int = Field(default=10, ge=1, le=1440)

app = FastAPI(title="NURA Flutter App Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if not secrets.compare_digest(x_api_key or "", API_TOKEN):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_api_key")

def seed(db: Session):
    if db.scalar(select(ClassSessionDB).limit(1)) is None:
        now = datetime.now(timezone.utc)
        db.add_all([
            ClassSessionDB(id="1", name="Boxing Fundamentals", trainer="Coach Mike", start_time=now + timedelta(days=1, hours=2), duration_minutes=60),
            ClassSessionDB(id="2", name="HIIT Training", trainer="Coach Sarah", start_time=now + timedelta(days=2), duration_minutes=45),
            ClassSessionDB(id="3", name="MMA Conditioning", trainer="Coach Alex", start_time=now + timedelta(days=3), duration_minutes=90),
            ClassSessionDB(id="4", name="Personal Training", trainer="Coach Elena", start_time=now + timedelta(days=4), duration_minutes=60),
        ])
    if db.scalar(select(WorkoutDB).limit(1)) is None:
        db.add_all([
            WorkoutDB(id="1", title="Boxing Fundamentals", description="Master boxing footwork and punches.", level="Beginner", duration="45 min", category="Boxing", image_url="https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=500"),
            WorkoutDB(id="2", title="Heavy Bag Power", description="High-intensity drills for explosive power.", level="Intermediate", duration="30 min", category="Boxing", image_url="https://images.unsplash.com/photo-1517438322351-db62136e01a0?w=500"),
            WorkoutDB(id="3", title="Full Body Strength", description="Compound lifts and functional movements.", level="Beginner", duration="60 min", category="Strength", image_url="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500"),
            WorkoutDB(id="4", title="HIIT Conditioning", description="Fast-paced circuits for conditioning.", level="Advanced", duration="25 min", category="HIIT", image_url="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500"),
        ])
    if db.scalar(select(SupplementDB).limit(1)) is None:
        db.add_all([
            SupplementDB(id="1", name="Whey Protein", description="Protein powder for recovery support.", price=39.99, category="Protein"),
            SupplementDB(id="2", name="Creatine Monohydrate", description="Performance supplement.", price=24.99, category="Performance"),
            SupplementDB(id="3", name="Electrolytes", description="Hydration support.", price=19.99, category="Hydration"),
        ])
    if db.get(MetricDB, 1) is None:
        db.add(MetricDB(id=1))
    if db.get(NutritionDB, 1) is None:
        db.add(NutritionDB(id=1))
    if db.scalar(select(MealDB).limit(1)) is None:
        db.add_all([MealDB(name="Breakfast", calories=520, time="8:00 AM"), MealDB(name="Lunch", calories=680, time="1:00 PM"), MealDB(name="Dinner", calories=650, time="7:00 PM")])
    if db.scalar(select(ProgressDB).limit(1)) is None:
        db.add_all([ProgressDB(kind="strength", x=i, y=y) for i, y in enumerate([100,105,103,110,115,120,125])])
        db.add_all([ProgressDB(kind="weight", x=i, y=y) for i, y in enumerate([85,84.5,84.2,83.8,83.5,83,82.5])])
    for provider in ["apple_health", "whoop", "garmin", "google_fit"]:
        if db.get(IntegrationDB, provider) is None:
            db.add(IntegrationDB(provider=provider, connected=False))
    db.commit()

@app.on_event("startup")
def startup():
    with SessionLocal() as db:
        seed(db)

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "nura-app-backend", "version": "1.0.0"}

@app.get("/api/v1/dashboard", dependencies=[Depends(require_api_key)])
def dashboard(db: Session = Depends(get_db)):
    m = db.get(MetricDB, 1)
    reservations = len(db.scalars(select(ClassSessionDB).where(ClassSessionDB.is_reserved.is_(True))).all())
    return {
        "readinessScore": m.readiness_score,
        "hrv": m.hrv,
        "sleepScore": m.sleep_score,
        "recoveryPercentage": m.recovery_percentage,
        "reservedClasses": reservations,
        "activeIntegrations": len(db.scalars(select(IntegrationDB).where(IntegrationDB.connected.is_(True))).all()),
    }

@app.get("/api/v1/metrics", dependencies=[Depends(require_api_key)])
def metrics(db: Session = Depends(get_db)):
    m = db.get(MetricDB, 1)
    strength = db.scalars(select(ProgressDB).where(ProgressDB.kind == "strength").order_by(ProgressDB.x)).all()
    weight = db.scalars(select(ProgressDB).where(ProgressDB.kind == "weight").order_by(ProgressDB.x)).all()
    return {
        "readinessScore": m.readiness_score,
        "hrv": m.hrv,
        "sleepScore": m.sleep_score,
        "recoveryPercentage": m.recovery_percentage,
        "strengthHistory": [{"x": p.x, "y": p.y} for p in strength],
        "weightHistory": [{"x": p.x, "y": p.y} for p in weight],
    }

@app.get("/api/v1/classes", dependencies=[Depends(require_api_key)])
def classes(db: Session = Depends(get_db)):
    rows = db.scalars(select(ClassSessionDB).order_by(ClassSessionDB.start_time)).all()
    return [{"id": r.id, "name": r.name, "startTime": r.start_time, "trainer": r.trainer, "durationMinutes": r.duration_minutes, "isReserved": r.is_reserved} for r in rows]

@app.post("/api/v1/classes/{class_id}/reserve", response_model=ReservationOut, dependencies=[Depends(require_api_key)])
def reserve(class_id: str, db: Session = Depends(get_db)):
    row = db.get(ClassSessionDB, class_id)
    if not row: raise HTTPException(404, "class_not_found")
    row.is_reserved = True; db.commit()
    return {"id": row.id, "isReserved": True}

@app.delete("/api/v1/classes/{class_id}/reserve", response_model=ReservationOut, dependencies=[Depends(require_api_key)])
def unreserve(class_id: str, db: Session = Depends(get_db)):
    row = db.get(ClassSessionDB, class_id)
    if not row: raise HTTPException(404, "class_not_found")
    row.is_reserved = False; db.commit()
    return {"id": row.id, "isReserved": False}

@app.get("/api/v1/workouts", dependencies=[Depends(require_api_key)])
def workouts(db: Session = Depends(get_db)):
    rows = db.scalars(select(WorkoutDB).order_by(WorkoutDB.id)).all()
    return [{"id": r.id, "title": r.title, "description": r.description, "level": r.level, "duration": r.duration, "imageUrl": r.image_url, "category": r.category} for r in rows]

@app.get("/api/v1/supplements", dependencies=[Depends(require_api_key)])
def supplements(db: Session = Depends(get_db)):
    rows = db.scalars(select(SupplementDB).order_by(SupplementDB.id)).all()
    return [{"id": r.id, "name": r.name, "description": r.description, "price": r.price, "imageUrl": r.image_url, "category": r.category} for r in rows]

@app.get("/api/v1/nutrition", dependencies=[Depends(require_api_key)])
def nutrition(db: Session = Depends(get_db)):
    n = db.get(NutritionDB, 1)
    meals = db.scalars(select(MealDB).order_by(MealDB.id)).all()
    return {"dailyCalories": n.daily_calories, "targetCalories": n.target_calories, "proteinGrams": n.protein_grams, "proteinTarget": n.protein_target, "carbsGrams": n.carbs_grams, "carbsTarget": n.carbs_target, "fatGrams": n.fat_grams, "fatTarget": n.fat_target, "meals": [{"id": m.id, "name": m.name, "calories": m.calories, "time": m.time, "imageUrl": m.image_url} for m in meals]}

@app.put("/api/v1/nutrition", dependencies=[Depends(require_api_key)])
def update_nutrition(payload: NutritionUpdate, db: Session = Depends(get_db)):
    n = db.get(NutritionDB, 1)
    mapping = {"dailyCalories":"daily_calories","targetCalories":"target_calories","proteinGrams":"protein_grams","proteinTarget":"protein_target","carbsGrams":"carbs_grams","carbsTarget":"carbs_target","fatGrams":"fat_grams","fatTarget":"fat_target"}
    for k, v in payload.model_dump(exclude_none=True).items(): setattr(n, mapping[k], v)
    db.commit(); return nutrition(db)

@app.post("/api/v1/nutrition/meals", dependencies=[Depends(require_api_key)])
def add_meal(payload: MealIn, db: Session = Depends(get_db)):
    row = MealDB(name=payload.name, calories=payload.calories, time=payload.time, image_url=payload.imageUrl)
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "name": row.name, "calories": row.calories, "time": row.time, "imageUrl": row.image_url}

@app.get("/api/v1/integrations", dependencies=[Depends(require_api_key)])
def integrations(db: Session = Depends(get_db)):
    rows = db.scalars(select(IntegrationDB).order_by(IntegrationDB.provider)).all()
    return [{"provider": r.provider, "connected": r.connected, "updatedAt": r.updated_at} for r in rows]

@app.put("/api/v1/integrations/{provider}", dependencies=[Depends(require_api_key)])
def update_integration(provider: str, payload: IntegrationIn, db: Session = Depends(get_db)):
    row = db.get(IntegrationDB, provider) or IntegrationDB(provider=provider)
    row.connected = payload.connected; row.updated_at = datetime.now(timezone.utc); db.add(row); db.commit()
    return {"provider": row.provider, "connected": row.connected, "updatedAt": row.updated_at}

@app.post("/api/v1/qr/pass", dependencies=[Depends(require_api_key)])
def create_qr_pass(payload: QRCreateIn, db: Session = Depends(get_db)):
    token = secrets.token_urlsafe(24)
    expires = datetime.now(timezone.utc) + timedelta(minutes=payload.ttlMinutes)
    db.add(QRPassDB(token=token, member_id=payload.memberId, expires_at=expires)); db.commit()
    return {"token": token, "memberId": payload.memberId, "expiresAt": expires}

@app.post("/api/v1/qr/validate", dependencies=[Depends(require_api_key)])
def validate_qr(payload: QRValidateIn, db: Session = Depends(get_db)):
    row = db.get(QRPassDB, payload.token)
    valid = bool(row and not row.revoked and row.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc))
    return {"valid": valid, "memberId": row.member_id if valid else None}

@app.get("/api/v1/admin/summary", dependencies=[Depends(require_api_key)])
def admin_summary(db: Session = Depends(get_db)):
    return {"classes": len(db.scalars(select(ClassSessionDB)).all()), "reservations": len(db.scalars(select(ClassSessionDB).where(ClassSessionDB.is_reserved.is_(True))).all()), "workouts": len(db.scalars(select(WorkoutDB)).all()), "supplements": len(db.scalars(select(SupplementDB)).all()), "integrationsConnected": len(db.scalars(select(IntegrationDB).where(IntegrationDB.connected.is_(True))).all())}

@app.post("/api/v1/ai-coach/analyze", dependencies=[Depends(require_api_key)])
def ai_coach_analyze():
    return {"status": "ready_for_model_integration", "message": "Backend contract is active. Connect pose-estimation/model service here; no autonomous health or medical decisions are performed by this endpoint."}
