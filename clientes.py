from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Cliente, get_db

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.post("/")
def crear_cliente(zona: int, entrada: int, habitaciones: int, banos: int, compania_id: int, db: Session = Depends(get_db)):
    cliente = Cliente(zona=zona, entrada=entrada, habitaciones=habitaciones, banos=banos, compania_id=compania_id)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente