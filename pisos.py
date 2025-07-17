from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import get_db, Piso
from utils import get_current_user

router = APIRouter(prefix="/pisos", tags=["pisos"])

class PisoCreate(BaseModel):
    precio: float
    tipo_vivienda: str | None
    habitaciones: int
    banos: str
    estado: str | None
    ascensor: str | None
    bajos: str | None
    entreplanta: str | None
    m2: int | None
    altura: str | None
    cercania_metro: str | None
    orientacion: str | None
    edificio_semi_nuevo: str | None
    adaptado_movilidad: str | None
    balcon: str | None
    patio: str | None
    terraza: str | None
    garaje: str | None
    trastero: str | None
    interior: str | None
    piscina: str | None
    urbanizacion: str | None
    vistas: str | None
    caracteristicas_adicionales: str | None

class PisoResponse(PisoCreate):
    id: int
    compania_id: int

@router.post("/", response_model=PisoResponse)
def create_piso(piso: PisoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_piso = Piso(**piso.dict(), compania_id=user.compania_id)
    db.add(db_piso)
    db.commit()
    db.refresh(db_piso)
    return db_piso

@router.get("/", response_model=list[PisoResponse])
def get_pisos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Piso).filter(Piso.compania_id == user.compania_id).all()
