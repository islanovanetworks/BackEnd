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
            if score >= 6:  # Umbral ajustable
                resultados.append({
                    "cliente_id": cliente.id,
                    "piso_id": piso.id,
                    "score": round(score, 2)
                })

    return resultados


def calcular_match(cliente, piso):
    score = 0

    # Zona
    if cliente.zona == piso.zona:
        score += 2

    # Precio
    capacidad = cliente.entrada * 10000  # Entrada en porcentaje
    if piso.precio <= capacidad:
        score += 3
    else:
        return 0  # No match posible

    # Habitaciones
    if piso.habitaciones >= cliente.habitaciones:
        score += 2

    # Baños
    if piso.banos >= cliente.banos:
        score += 1

    # Tipo de vivienda
    if not cliente.tipo or cliente.tipo == piso.tipo:
        score += 1

    # Estado
    if not cliente.estado or cliente.estado == piso.estado:
        score += 1

    # Situación
    if not cliente.situacion or cliente.situacion == piso.situacion:
        score += 1

    # Ascensor
    if not cliente.ascensor or cliente.ascensor == piso.ascensor:
        score += 0.5

    # Planta
    if not cliente.planta or cliente.planta == piso.planta:
        score += 0.5

    # Extras booleanos (si == "Si")
    extras = ["balcon", "terraza", "patio", "bajo", "garaje", "trastero"]
    for campo in extras:
        valor_cliente = getattr(cliente, campo, None)
        valor_piso = getattr(piso, campo, None)
        if valor_cliente == "Si" and valor_piso == "Si":
            score += 0.5

    return score
