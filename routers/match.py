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
            score = calcular_match_score(cliente, piso)
            if score > 0:  # Only include matches with positive scores
                resultados.append({
                    "cliente_id": cliente.id,
                    "piso_id": piso.id,
                    "score": round(score, 2)
                })

    # Sort by score in descending order
    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados

def calcular_match_score(cliente, piso):
    score = 0
    max_score = 100

    # Must-have criteria (if these fail, return 0)
    if cliente.zona != piso.zona:
        return 0
    capacidad = cliente.ahorro * 10  # Assuming ahorro is a percentage of price
    if piso.precio > capacidad:
        return 0
    if piso.habitaciones < cliente.habitaciones:
        return 0
    if piso.banos < cliente.banos:
        return 0

    # Weighted criteria
    weights = {
        "tipo_vivienda": 15,
        "estado": 10,
        "ascensor": 8,
        "m2": 10,
        "altura": 7,
        "cercania_metro": 7,
        "orientacion": 5,
        "edificio_semi_nuevo": 5,
        "adaptado_movilidad": 5,
        "balcon": 5,
        "patio": 5,
        "terraza": 5,
        "garaje": 5,
        "trastero": 5,
        "piscina": 3,
        "urbanizacion": 3,
        "vistas": 2
    }

    # Match each field
    if cliente.tipo_vivienda == piso.tipo_vivienda:
        score += weights["tipo_vivienda"]
    if cliente.estado == piso.estado:
        score += weights["estado"]
    if cliente.ascensor == piso.ascensor:
        score += weights["ascensor"]
    if abs(cliente.m2 - piso.m2) <= 10:  # Within 10m²
        score += weights["m2"]
    if cliente.altura == piso.altura:
        score += weights["altura"]
    if cliente.cercania_metro == piso.cercania_metro:
        score += weights["cercania_metro"]
    if cliente.orientacion == piso.orientacion:
        score += weights["orientacion"]
    if cliente.edificio_semi_nuevo == piso.edificio_semi_nuevo:
        score += weights["edificio_semi_nuevo"]
    if cliente.adaptado_movilidad == piso.adaptado_movilidad:
        score += weights["adaptado_movilidad"]
    if cliente.balcon == piso.balcon:
        score += weights["balcon"]
    if cliente.patio == piso.patio:
        score += weights["patio"]
    if cliente.terraza == piso.terraza:
        score += weights["terraza"]
    if cliente.garaje == piso.garaje:
        score += weights["garaje"]
    if cliente.trastero == piso.trastero:
        score += weights["trastero"]
    if cliente.piscina == piso.piscina:
        score += weights["piscina"]
    if cliente.urbanizacion == piso.urbanizacion:
        score += weights["urbanizacion"]
    if cliente.vistas == piso.vistas:
        score += weights["vistas"]

    return (score / max_score) * 100
