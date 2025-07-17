from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import get_db, Usuario, Compania
from passlib.context import CryptContext

router = APIRouter(prefix="/register", tags=["register"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    compania = db.query(Compania).filter(Compania.id == usuario.compania_id).first()
    if not compania:
        raise HTTPException(status_code=404, detail="Compañía no encontrada")
    existing_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    db_usuario = Usuario(email=usuario.email, password=pwd_context.hash(usuario.password), compania_id=usuario.compania_id)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario
