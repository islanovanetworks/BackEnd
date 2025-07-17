from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, Cliente, Piso
from utils import get_current_user

router = APIRouter(prefix="/match", tags=["match"])

@router.get("/")
def obtener_matches(db: Session = Depends(get_db), user=Depends(get_current_user)):
    clientes = db.query(Cliente).filter(Cliente.compania_id == user.compania_id).all()
    pisos = db.query(Piso).filter(Piso.compania_id == user.compania_id).all()

    resultados = []

    for cliente in clientes:
        for piso in pisos:
            score = calcular_match(cliente, piso)
            if score >= 3:  # umbral ajustable
                resultados.append({
                    "cliente_id": cliente.id,
                    "piso_id": piso.id,
                    "score": score
                })

    return resultados
