from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models import get_db, Cliente
from utils import get_current_user

router = APIRouter(prefix="/clientes", tags=["clientes"])

class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    zona: str
    subzonas: Optional[str]
    entrada: float
    precio: float
    tipo_vivienda: Optional[str]
    finalidad: Optional[str]
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
    banco: Optional[str]
    ahorro: float
    compania_id: int

class ClienteResponse(BaseModel):
    id: int
    nombre: str
    telefono: str
    zona: str
    subzonas: Optional[str]
    entrada: float
    precio: float
    tipo_vivienda: Optional[str]
    finalidad: Optional[str]
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
    banco: Optional[str]
    ahorro: float
    compania_id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=ClienteResponse)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if cliente.compania_id != current_user.compania_id:
        raise HTTPException(status_code=403, detail="Not authorized to create cliente for this compania")
    db_cliente = Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.get("/", response_model=list[ClienteResponse])
def read_clientes(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    clientes = db.query(Cliente).filter(Cliente.compania_id == current_user.compania_id).all()
    return clientes
