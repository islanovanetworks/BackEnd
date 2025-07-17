from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import get_db, Usuario, Compania
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
def register(email: str, password: str, nombre_compania: str, db: Session = Depends(get_db)):
    # 1. Comprobar si la compañía ya existe
    if db.query(Compania).filter(Compania.nombre == nombre_compania).first():
        raise HTTPException(status_code=400, detail="Compañía ya registrada")

    # 2. Crear compañía
    nueva_compania = Compania(nombre=nombre_compania)
    db.add(nueva_compania)
    db.commit()
    db.refresh(nueva_compania)

    # 3. Crear usuario vinculado
    hashed_pw = pwd_context.hash(password)
    nuevo_usuario = Usuario(email=email, hashed_password=hashed_pw, compania_id=nueva_compania.id)
    db.add(nuevo_usuario)
    db.commit()

    return {"msg": "Registrado correctamente"}
