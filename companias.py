from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Compania, get_db

router = APIRouter(prefix="/companias", tags=["companias"])

@router.post("/")
def create_compania(nombre: str, db: Session = Depends(get_db)):
    existing = db.query(Compania).filter(Compania.nombre == nombre).first()
    if existing:
        raise HTTPException(status_code=400, detail="Compañía ya existe")
    compania = Compania(nombre=nombre)
    db.add(compania)
    db.commit()
    db.refresh(compania)
    return compania