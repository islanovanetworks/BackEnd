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
