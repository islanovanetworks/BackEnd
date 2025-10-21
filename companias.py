from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import get_db, Compania

router = APIRouter(prefix="/companias", tags=["companias"])

class CompaniaCreate(BaseModel):
    nombre: str

class CompaniaResponse(CompaniaCreate):
    id: int

@router.post("/", response_model=CompaniaResponse)
def create_compania(compania: CompaniaCreate, db: Session = Depends(get_db)):
    db_compania = Compania(**compania.dict())
    db.add(db_compania)
    db.commit()
    db.refresh(db_compania)
    return db_compania

@router.get("/", response_model=list[CompaniaResponse])
def get_companias(db: Session = Depends(get_db)):
    return db.query(Compania).all()

@router.get("/{compania_id}/trial-status")
def check_trial_status(compania_id: int, db: Session = Depends(get_db)):
    """Verificar si la prueba gratuita de una compañía está activa"""
    from datetime import datetime
    
    compania = db.query(Compania).filter(Compania.id == compania_id).first()
    if not compania:
        raise HTTPException(status_code=404, detail="Compañía no encontrada")
    
    # Si no tiene fecha de caducidad, está activa
    if not compania.fecha_caducidad_trial:
        return {"trial_active": True, "fecha_caducidad": None}
    
    # Comparar fecha actual con fecha de caducidad
    fecha_actual = datetime.now().date()
    fecha_caducidad = datetime.strptime(compania.fecha_caducidad_trial, "%Y-%m-%d").date()
    
    trial_active = fecha_actual <= fecha_caducidad
    
    return {
        "trial_active": trial_active,
        "fecha_caducidad": compania.fecha_caducidad_trial,
        "dias_restantes": (fecha_caducidad - fecha_actual).days if trial_active else 0
    }
