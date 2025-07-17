from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import get_db, Usuario, Compania

router = APIRouter(prefix="/register", tags=["register"])

class UsuarioCreate(BaseModel):
    email: str
    password: str
    compania_id: int

class UsuarioResponse(BaseModel):
    id: int
    email: str
    compania_id: int

@router.post("/", response_model=UsuarioResponse)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Check if company exists
    compania = db.query(Compania).filter(Compania.id == usuario.compania_id).first()
    if not compania:
        raise HTTPException(status_code=404, detail="Compañía no encontrada")
    # Check if email is already registered
    existing_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    # Create user (password should be hashed in production)
    db_usuario = Usuario(email=usuario.email, password=usuario.password, compania_id=usuario.compania_id)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario
