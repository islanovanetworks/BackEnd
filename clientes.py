from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import get_db, Cliente
from utils import get_current_user

router = APIRouter(prefix="/clientes", tags=["clientes"])

class ClienteCreate(BaseModel):
    nombre: str | None
    telefono: str | None
    zona: str
    subzonas: str | None
    entrada: float
    precio: float | None
    tipo_vivienda: str | None
    finalidad: str | None
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
    banco: str | None
    ahorro: float | None

class ClienteResponse(ClienteCreate):
    id: int
    compania_id: int

@router.post("/", response_model=ClienteResponse)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_cliente = Cliente(**cliente.dict(), compania_id=user.compania_id)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.get("/", response_model=list[ClienteResponse])
def get_clientes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Cliente).filter(Cliente.compania_id == user.compania_id).all()
