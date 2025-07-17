from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models import get_db, Piso
from utils import get_current_user

router = APIRouter(prefix="/pisos", tags=["pisos"])

class PisoCreate(BaseModel):
    precio: float
    tipo_vivienda: Optional[str]
    habitaciones: int
    banos: Optional[str]
    estado: Optional[str]
    ascensor: Optional[str]
    bajos: Optional[str]
    entreplanta: Optional[str]
    m2: int
    altura: Optional[str]
    cercania_metro: Optional[str]
    orientacion: Optional[str]
    edificio_semi_nuevo: Optional[str]
    adaptado_movilidad: Optional[str]
    balcon: Optional[str]
    patio: Optional[str]
    terraza: Optional[str]
    garaje: Optional[str]
    trastero: Optional[str]
    interior: Optional[str]
    piscina: Optional[str]
    urbanizacion: Optional[str]
    vistas: Optional[str]
    caracteristicas_adicionales: Optional[str]
    compania_id: int

class PisoResponse(BaseModel):
    id: int
    precio: float
    tipo_vivienda: Optional[str]
    habitaciones: int
    banos: Optional[str]
    estado: Optional[str]
    ascensor: Optional[str]
    bajos: Optional[str]
    entreplanta: Optional[str]
    m2: int
    altura: Optional[str]
    cercania_metro: Optional[str]
    orientacion: Optional[str]
    edificio_semi_nuevo: Optional[str]
    adaptado_movilidad: Optional[str]
    balcon: Optional[str]
    patio: Optional[str]
    terraza: Optional[str]
    garaje: Optional[str]
    trastero: Optional[str]
    interior: Optional[str]
    piscina: Optional[str]
    urbanizacion: Optional[str]
    vistas: Optional[str]
    caracteristicas_adicionales: Optional[str]
    compania_id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=PisoResponse)
def create_piso(piso: PisoCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if piso.compania_id != current_user.compania_id:
        raise HTTPException(status_code=403, detail="Not authorized to create piso for this compania")
    db_piso = Piso(**piso.dict())
    db.add(db_piso)
    db.commit()
    db.refresh(db_piso)
    return db_piso

@router.get("/", response_model=list[PisoResponse])
def read_pisos(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    pisos = db.query(Piso).filter(Piso.compania_id == current_user.compania_id).all()
    return pisos
