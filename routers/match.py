from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import get_db, Cliente, Piso
from utils import get_current_user

router = APIRouter(prefix="/match", tags=["match"])

class MatchResponse(BaseModel):
    cliente_id: int
    piso_id: int
    score: float  # Always 100% for exact matches

def get_price_range(precio: float) -> tuple:
    """Calculate the price range for matching."""
    if precio <= 200000:
        return precio, precio + 9999  # €10,000 increments up to €200,000
    else:
        increment = 20000
        upper = ((precio // increment) + 1) * increment - 1
        return precio, upper

def get_m2_range(m2: int) -> tuple:
    """Calculate the m2 range for matching."""
    valid_m2 = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 150]
    if m2 not in valid_m2:
        return m2, 150  # Default to max if invalid
    return m2, 150

@router.get("/", response_model=list[MatchResponse])
def obtener_matches(piso_id: int = None, cliente_id: int = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if piso_id and cliente_id:
        raise HTTPException(status_code=400, detail="Provide either piso_id or cliente_id, not both")
    if not (piso_id or cliente_id):
        raise HTTPException(status_code=400, detail="Provide either piso_id or cliente_id")

    matches = []
    
    if piso_id:
        piso = db.query(Piso).filter(Piso.id == piso_id, Piso.compania_id == user.compania_id).first()
        if not piso:
            raise HTTPException(status_code=404, detail="Piso no encontrado")
        clientes = db.query(Cliente).filter(Cliente.compania_id == user.compania_id).all()
        for cliente in clientes:
            if is_exact_match_piso_to_cliente(piso, cliente):
                matches.append(MatchResponse(cliente_id=cliente.id, piso_id=piso.id, score=100.0))
    
    elif cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.compania_id == user.compania_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        pisos = db.query(Piso).filter(Piso.compania_id == user.compania_id).all()
        for piso in pisos:
            if is_exact_match_piso_to_cliente(piso, cliente):
                matches.append(MatchResponse(cliente_id=cliente.id, piso_id=piso.id, score=100.0))
    
    return matches

def is_exact_match_piso_to_cliente(piso: Piso, cliente: Cliente) -> bool:
    """Check if a piso exactly matches a cliente's criteria."""
    # Zona: At least one zone must match
    cliente_zonas = set(cliente.zona.split(",") if cliente.zona else [])
    piso_zonas = set(piso.zona.split(",") if piso.zona else [])
    if not cliente_zonas.intersection(piso_zonas):
        return False
    
    # Precio: Piso price must be within client's range
    cliente_precio_min, cliente_precio_max = get_price_range(cliente.precio)
    if not (cliente_precio_min <= piso.precio <= cliente_precio_max):
        return False
    
    # Metros Cuadrados: Piso m2 must be within client's range
    cliente_m2_min, cliente_m2_max = get_m2_range(cliente.m2)
    if not (cliente_m2_min <= piso.m2 <= cliente_m2_max):
        return False
    
    # Exact matches for multi-select fields
    # Exact matches for multi-select fields (excluding orientacion which is now optional)
    for field in ["tipo_vivienda", "finalidad", "habitaciones", "banos"]:
        cliente_values = set(cliente.__dict__[field].split(",") if cliente.__dict__[field] else [])
        piso_values = set(piso.__dict__[field].split(",") if piso.__dict__[field] else [])
        if cliente_values and not cliente_values.issubset(piso_values):
            return False
    
    # Orientación: Optional matching - only check if both have values
    cliente_orientacion = set(cliente.orientacion.split(",") if cliente.orientacion else [])
    piso_orientacion = set(piso.orientacion.split(",") if piso.orientacion else [])
    if cliente_orientacion and piso_orientacion and not cliente_orientacion.intersection(piso_orientacion):
        return False
    
    # Exact matches for single-select fields
    for field in [
        "estado", "ascensor", "bajos", "entreplanta", "altura", "cercania_metro",
        "edificio_semi_nuevo", "adaptado_movilidad", "balcon", "patio", "terraza",
        "garaje", "trastero", "interior", "piscina", "urbanizacion", "vistas",
        "caracteristicas_adicionales", "permuta"
    ]:
        cliente_value = cliente.__dict__[field]
        piso_value = piso.__dict__[field]
        if cliente_value and cliente_value != piso_value:
            return False
    
    return True
