from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import get_db, Cliente, Piso
from utils import get_current_user

router = APIRouter(prefix="/match", tags=["match"])

@router.get("/")
def obtener_matches(piso_id: int = None, cliente_id: int = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if piso_id:
        piso = db.query(Piso).filter(Piso.id == piso_id, Piso.compania_id == user.compania_id).first()
        if not piso:
            raise HTTPException(status_code=404, detail="Piso no encontrado")
        clientes = db.query(Cliente).filter(Cliente.compania_id == user.compania_id).all()
        resultados = [
            {"cliente_id": cliente.id, "piso_id": piso.id, "score": round(calcular_match_score(cliente, piso), 2)}
            for cliente in clientes if calcular_match_score(cliente, piso) > 0
        ]
    elif cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.compania_id == user.compania_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        pisos = db.query(Piso).filter(Piso.compania_id == user.compania_id).all()
        resultados = [
            {"cliente_id": cliente.id, "piso_id": piso.id, "score": round(calcular_match_score(cliente, piso), 2)}
            for piso in pisos if calcular_match_score(cliente, piso) > 0
        ]
    else:
        clientes = db.query(Cliente).filter(Cliente.compania_id == user.compania_id).all()
        pisos = db.query(Piso).filter(Piso.compania_id == user.compania_id).all()
        resultados = [
            {"cliente_id": cliente.id, "piso_id": piso.id, "score": round(calcular_match_score(cliente, piso), 2)}
            for cliente in clientes for piso in pisos if calcular_match_score(cliente, piso) > 0
        ]

    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados

def calcular_match_score(cliente, piso):
    score = 0
    max_score = 100

    # Must-have criteria
    if cliente.zona and piso.zona and cliente.zona != piso.zona:
        return 0
    capacidad = (cliente.ahorro or 0) * 10  # Assuming ahorro is a percentage of price
    if piso.precio and piso.precio > capacidad:
        return 0
    if cliente.habitaciones and piso.habitaciones and piso.habitaciones < cliente.habitaciones:
        return 0
    if cliente.banos and piso.banos and cliente.banos != piso.banos:
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
        "interior": 3,
        "piscina": 3,
        "urbanizacion": 3,
        "vistas": 2
    }

    if cliente.tipo_vivienda and piso.tipo_vivienda and cliente.tipo_vivienda == piso.tipo_vivienda:
        score += weights["tipo_vivienda"]
    if cliente.estado and piso.estado and cliente.estado == piso.estado:
        score += weights["estado"]
    if cliente.ascensor and piso.ascensor and cliente.ascensor == piso.ascensor:
        score += weights["ascensor"]
    if cliente.m2 and piso.m2 and abs(cliente.m2 - piso.m2) <= 10:
        score += weights["m2"]
    if cliente.altura and piso.altura and cliente.altura == piso.altura:
        score += weights["altura"]
    if cliente.cercania_metro and piso.cercania_metro and cliente.cercania_metro == piso.cercania_metro:
        score += weights["cercania_metro"]
    if cliente.orientacion and piso.orientacion and cliente.orientacion == piso.orientacion:
        score += weights["orientacion"]
    if cliente.edificio_semi_nuevo and piso.edificio_semi_nuevo and cliente.edificio_semi_nuevo == piso.edificio_semi_nuevo:
        score += weights["edificio_semi_nuevo"]
    if cliente.adaptado_movilidad and piso.adaptado_movilidad and cliente.adaptado_movilidad == piso.adaptado_movilidad:
        score += weights["adaptado_movilidad"]
    if cliente.balcon and piso.balcon and cliente.balcon == piso.balcon:
        score += weights["balcon"]
    if cliente.patio and piso.patio and cliente.patio == piso.patio:
        score += weights["patio"]
    if cliente.terraza and piso.terraza and cliente.terraza == piso.terraza:
        score += weights["terraza"]
    if cliente.garaje and piso.garaje and cliente.garaje == piso.garaje:
        score += weights["garaje"]
    if cliente.trastero and piso.trastero and cliente.trastero == piso.trastero:
        score += weights["trastero"]
    if cliente.interior and piso.interior and cliente.interior == piso.interior:
        score += weights["interior"]
    if cliente.piscina and piso.piscina and cliente.piscina == piso.piscina:
        score += weights["piscina"]
    if cliente.urbanizacion and piso.urbanizacion and cliente.urbanizacion == piso.urbanizacion:
        score += weights["urbanizacion"]
    if cliente.vistas and piso.vistas and cliente.vistas == piso.vistas:
        score += weights["vistas"]

    return (score / max_score) * 100
