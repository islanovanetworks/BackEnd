from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario, Compania, get_db
from passlib.context import CryptContext

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/")
def create_usuario(email: str, password: str, compania_id: int, db: Session = Depends(get_db)):
    existing = db.query(Usuario).filter(Usuario.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    hashed_password = pwd_context.hash(password)
    user = Usuario(email=email, hashed_password=hashed_password, compania_id=compania_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user