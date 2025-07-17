from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import get_db, Piso
from utils import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/pisos", tags=["pisos"])

class PisoCreate(BaseModel):
    precio: float
    tipo_vivienda: str
    habitaciones: int
    banos: str
    estado: str
    ascensor: str
    bajos: str
    entreplanta: str
    m2: int
    altura: str
    cercania_metro: str
    orientacion: str
    edificio_semi_nuevo: str
    adaptado_movilidad: str
    balcon: str
    patio: str
    terraza: str
    garaje: str
    trastero: str
    interior: str
    piscina: str
    urbanizacion: str
    vistas: str
    caracteristicas_adicionales: str

@router.post("/", response_model=PisoCreate)
def create_piso(piso: PisoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_piso = Piso(**piso.dict(), compania_id=user.compania_id)
    db.add(db_piso)
    db.commit()
    db.refresh(db_piso)
    return db_piso
