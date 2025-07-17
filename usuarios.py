from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import get_db, Usuario
from utils import get_current_user

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

class UsuarioResponse(BaseModel):
    id: int
    email: str
    compania_id: int

@router.get("/", response_model=list[UsuarioResponse])
def get_usuarios(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Usuario).filter(Usuario.compania_id == user.compania_id).all()
