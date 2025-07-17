from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import get_db, Cliente
from utils import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/clientes", tags=["clientes"])

class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    zona: str
    subzonas: str
    precio: float
    tipo_vivienda: str
    finalidad: str
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
    banco: str
    ahorro: float

@router.post("/", response_model=ClienteCreate)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_cliente = Cliente(**cliente.dict(), compania_id=user.compania_id)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente
