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
            if match_basico(cliente, piso):
                resultados.append({
                    "cliente_id": cliente.id,
                    "piso_id": piso.id
                })

    return resultados


def match_basico(cliente, piso):
    # ZONA debe coincidir
    if cliente.zona != piso.zona:
        return False

    # Precio del piso debe estar por debajo del presupuesto del cliente
    capacidad = cliente.entrada * 10000  # Entrada como % del precio
    if piso.precio > capacidad:
        return False

    # Habitaciones mínimas
    if piso.habitaciones < cliente.habitaciones:
        return False

    # Baños mínimos
    if piso.banos < cliente.banos:
        return False

    return True
