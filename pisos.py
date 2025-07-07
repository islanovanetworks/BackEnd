from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Piso, get_db

router = APIRouter(prefix="/pisos", tags=["pisos"])

@router.post("/")
def crear_piso(zona: int, precio: int, habitaciones: int, banos: int, compania_id: int, db: Session = Depends(get_db)):
    piso = Piso(zona=zona, precio=precio, habitaciones=habitaciones, banos=banos, compania_id=compania_id)
    db.add(piso)
    db.commit()
    db.refresh(piso)
    return piso