from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import get_db, Usuario
from utils import get_current_user

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

class UsuarioResponse(BaseModel):
    id: int
    email: str
    rol: str
    compania_id: int

@router.get("/", response_model=list[UsuarioResponse])
def get_usuarios(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Solo Supervisores pueden ver la lista de usuarios
    if current_user.rol != "Supervisor":
        raise HTTPException(status_code=403, detail="Se requieren permisos de Supervisor")
    
    return db.query(Usuario).filter(Usuario.compania_id == current_user.compania_id).all()
