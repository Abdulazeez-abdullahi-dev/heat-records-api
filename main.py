from datetime import datetime
from typing import Optional

from fastapi.responses import HTMLResponse
from page import PAGE

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        create_engine)
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker
from sqlalchemy import func

# ---------- Database ----------
engine = create_engine("sqlite:///heats.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class Heat(Base):
    __tablename__ = "heats"
    id = Column(Integer, primary_key=True)
    heat_no = Column(String, unique=True, index=True, nullable=False)
    furnace = Column(String, nullable=False)          # "EAF" or "LRF"
    grade = Column(String, index=True)
    shift = Column(String)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    tap_temp = Column(Float)                           # deg C
    power_kwh = Column(Float)
    electrode_kg = Column(Float)
    tap_weight_t = Column(Float)
    oxygen_nm3 = Column(Float)
    events = relationship("HeatEvent", back_populates="heat", cascade="all, delete-orphan")


class HeatEvent(Base):
    __tablename__ = "heat_events"
    id = Column(Integer, primary_key=True)
    heat_id = Column(Integer, ForeignKey("heats.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    kind = Column(String, nullable=False)              # temperature | sample | addition
    c = Column(Float)
    mn = Column(Float)
    si = Column(Float)
    s = Column(Float)
    p = Column(Float)
    temperature = Column(Float)
    note = Column(String)
    heat = relationship("Heat", back_populates="events")


Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Schemas (validation) ----------
class EventIn(BaseModel):
    timestamp: datetime
    kind: str = Field(pattern="^(temperature|sample|addition)$")
    c: Optional[float] = Field(None, ge=0, le=5)
    mn: Optional[float] = Field(None, ge=0, le=5)
    si: Optional[float] = Field(None, ge=0, le=5)
    s: Optional[float] = Field(None, ge=0, le=1)
    p: Optional[float] = Field(None, ge=0, le=1)
    temperature: Optional[float] = Field(None, ge=1000, le=1800)
    note: Optional[str] = None


class EventOut(EventIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class HeatIn(BaseModel):
    heat_no: str = Field(min_length=1)
    furnace: str = Field(pattern="^(EAF|LRF)$")
    grade: Optional[str] = None
    shift: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tap_temp: Optional[float] = Field(None, ge=1400, le=1800)
    power_kwh: Optional[float] = Field(None, ge=0)
    electrode_kg: Optional[float] = Field(None, ge=0)
    tap_weight_t: Optional[float] = Field(None, ge=0, le=300)
    oxygen_nm3 : Optional[float] = Field(None, ge=0, le=3000)


class HeatUpdate(BaseModel):
    grade: Optional[str] = None
    shift: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tap_temp: Optional[float] = Field(None, ge=1400, le=1800)
    power_kwh: Optional[float] = Field(None, ge=0)
    electrode_kg: Optional[float] = Field(None, ge=0)
    tap_weight_t: Optional[float] = Field(None, ge=0, le=300)
    oxygen_nm3 : Optional[float] = Field(None, ge=0, le=3000)


class HeatOut(HeatIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class HeatDetail(HeatOut):
    events: list[EventOut] = []


# ---------- API ----------
app = FastAPI(title="Heat Records API")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return PAGE


def find_heat(db: Session, heat_no: str) -> Heat:
    heat = db.query(Heat).filter(Heat.heat_no == heat_no).first()
    if not heat:
        raise HTTPException(404, "Heat not found")
    return heat


@app.get("/heats", response_model=list[HeatOut])
def list_heats(
    furnace: Optional[str] = None,
    grade: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Heat)
    if furnace:
        q = q.filter(Heat.furnace == furnace)
    if grade:
        q = q.filter(Heat.grade == grade)
    if date_from:
        q = q.filter(Heat.start_time >= date_from)
    if date_to:
        q = q.filter(Heat.start_time <= date_to)
    return q.order_by(Heat.start_time.desc()).offset(offset).limit(limit).all()


@app.get("/heats/{heat_no}", response_model=HeatDetail)
def get_heat(heat_no: str, db: Session = Depends(get_db)):
    return find_heat(db, heat_no)


@app.post("/heats", response_model=HeatOut, status_code=201)
def create_heat(data: HeatIn, db: Session = Depends(get_db)):
    if db.query(Heat).filter(Heat.heat_no == data.heat_no).first():
        raise HTTPException(409, "Heat number already exists")
    heat = Heat(**data.model_dump())
    db.add(heat)
    db.commit()
    db.refresh(heat)
    return heat


@app.patch("/heats/{heat_no}", response_model=HeatOut)
def update_heat(heat_no: str, data: HeatUpdate, db: Session = Depends(get_db)):
    heat = find_heat(db, heat_no)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(heat, key, value)
    db.commit()
    db.refresh(heat)
    return heat


@app.post("/heats/{heat_no}/events", response_model=EventOut, status_code=201)
def add_event(heat_no: str, data: EventIn, db: Session = Depends(get_db)):
    heat = find_heat(db, heat_no)
    event = HeatEvent(heat_id=heat.id, **data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.delete("/heats/{heat_no}", status_code=204)
def delete_heat(heat_no: str, db: Session = Depends(get_db)):
    db.delete(find_heat(db, heat_no))
    db.commit()


@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    rows = (
        db.query(Heat.grade, func.count(Heat.id), func.avg(Heat.tap_temp))
        .group_by(Heat.grade)
        .all()
    )
    return [
        {"grade": g, "heats": n, "avg_tap_temp": round(t, 1) if t else None}
        for g, n, t in rows
    ]