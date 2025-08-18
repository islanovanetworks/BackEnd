from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import get_db, Cliente, Piso
from utils import get_current_user

router = APIRouter(prefix="/match", tags=["match"])

class MatchResponse(BaseModel):
    cliente_id: int
    piso_id: int
    score: int  # Score from 50 to 100

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
            score = calculate_match_score(piso, cliente)
            if score >= 50:  # Only show matches with 50% or higher
                matches.append(MatchResponse(cliente_id=cliente.id, piso_id=piso.id, score=score))
    
    elif cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.compania_id == user.compania_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        pisos = db.query(Piso).filter(Piso.compania_id == user.compania_id).all()
        for piso in pisos:
            score = calculate_match_score(piso, cliente)
            if score >= 50:  # Only show matches with 50% or higher
                matches.append(MatchResponse(cliente_id=cliente.id, piso_id=piso.id, score=score))
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x.score, reverse=True)
    return matches

def calculate_match_score(piso: Piso, cliente: Cliente) -> int:
    """Calculate match score based on penalty system (starts at 100%, penalties reduce score)."""
    try:
        score = 100  # Start with 100%
        
        # PARÁMETROS IMPORTANTES (10% penalty each)
        
        # 1. Zona: At least one zone must match
        if not check_zona_match(piso, cliente):
            score -= 10
        
        # 2. Habitaciones: Piso habitaciones >= Cliente habitaciones
        habitaciones_penalty = check_habitaciones_match(piso, cliente)
        if habitaciones_penalty > 0:
            score -= 10  # Exclude if no match
            return 0  # Exclude directly
        
        # 3. Estado: At least one value must match
        if not check_estado_match(piso, cliente):
            score -= 10
        
        # 4. Tipo de Vivienda: At least one value must match
        if not check_tipo_vivienda_match(piso, cliente):
            score -= 10
        
        # 5. Bajos: Exact match required
        if not check_bajos_match(piso, cliente):
            score -= 10
        
        # 6. Entreplantas: Exact match required
        if not check_entreplanta_match(piso, cliente):
            score -= 10
        
        # PARÁMETROS MEDIOS (5% penalty each)
        
        # 1. Precio: Complex penalty system
        precio_penalty = check_precio_match(piso, cliente)
        if precio_penalty == -1:  # Exclude directly
            return 0
        score -= precio_penalty
        
        # 2. Metros Cuadrados: Complex penalty system  
        m2_penalty = check_m2_match(piso, cliente)
        if m2_penalty == -1:  # Exclude directly
            return 0
        score -= m2_penalty
        
        # 3. Ascensor: Complex penalty system
        ascensor_penalty = check_ascensor_match(piso, cliente)
        if ascensor_penalty == -1:  # Exclude directly
            return 0
        score -= ascensor_penalty
        
        # 4. Cercanía Metro: Complex penalty system
        metro_penalty = check_cercania_metro_match(piso, cliente)
        score -= metro_penalty
        
        # 5. Altura: 5% penalty if different
        if not check_altura_match(piso, cliente):
            score -= 5
        
        # 6. Interior: 5% penalty if different
        if not check_interior_match(piso, cliente):
            score -= 5
        
        # 7. Balcón/Terraza: 5% penalty if client wants and piso doesn't have
        balcon_penalty = check_balcon_terraza_match(piso, cliente)
        score -= balcon_penalty
        
        # 8. Patio: 5% penalty if client wants and piso doesn't have
        patio_penalty = check_patio_match(piso, cliente)
        score -= patio_penalty
        
        return max(score, 0)  # Ensure score doesn't go below 0
        
    except Exception as e:
        print(f"Error in scoring: {str(e)}")
        return 0

def check_zona_match(piso: Piso, cliente: Cliente) -> bool:
    """Check if at least one zone matches."""
    cliente_zonas = set(cliente.zona.split(",") if cliente.zona else [])
    piso_zonas = set(piso.zona.split(",") if piso.zona else [])
    return bool(cliente_zonas.intersection(piso_zonas))

def check_habitaciones_match(piso: Piso, cliente: Cliente) -> int:
    """Check habitaciones match. Returns penalty (0 = match, >0 = penalty)."""
    if not cliente.habitaciones:
        return 0  # No preference
    
    cliente_habitaciones = [int(x) for x in cliente.habitaciones.split(",") if x.strip()]
    if not cliente_habitaciones:
        return 0
    
    if not piso.habitaciones:
        return 1  # Exclude if piso doesn't specify
    
    piso_habitaciones = [int(x) for x in piso.habitaciones.split(",") if x.strip()]
    if not piso_habitaciones:
        return 1
    
    # Check if piso has at least the minimum required by cliente
    min_cliente = min(cliente_habitaciones)
    max_piso = max(piso_habitaciones)
    
    if max_piso >= min_cliente:
        return 0  # Match
    else:
        return 1  # Exclude

def check_estado_match(piso: Piso, cliente: Cliente) -> bool:
    """Check if at least one estado value matches."""
    if not cliente.estado:
        return True  # No preference
    
    cliente_estados = set(cliente.estado.split(",") if cliente.estado else [])
    piso_estados = set(piso.estado.split(",") if piso.estado else [])
    
    if not cliente_estados:
        return True
    if not piso_estados:
        return False
    
    return bool(cliente_estados.intersection(piso_estados))

def check_tipo_vivienda_match(piso: Piso, cliente: Cliente) -> bool:
    """Check if at least one tipo_vivienda value matches."""
    if not cliente.tipo_vivienda:
        return True  # No preference
    
    cliente_tipos = set(cliente.tipo_vivienda.split(",") if cliente.tipo_vivienda else [])
    piso_tipos = set(piso.tipo_vivienda.split(",") if piso.tipo_vivienda else [])
    
    if not cliente_tipos:
        return True
    if not piso_tipos:
        return False
    
    return bool(cliente_tipos.intersection(piso_tipos))

def check_bajos_match(piso: Piso, cliente: Cliente) -> bool:
    """Check exact match for bajos."""
    if not cliente.bajos:
        return True  # No preference
    return cliente.bajos == piso.bajos

def check_entreplanta_match(piso: Piso, cliente: Cliente) -> bool:
    """Check exact match for entreplanta."""
    if not cliente.entreplanta:
        return True  # No preference
    return cliente.entreplanta == piso.entreplanta

def check_precio_match(piso: Piso, cliente: Cliente) -> int:
    """Check precio match. Returns penalty (0, 5, 10) or -1 to exclude."""
    if not piso.precio or not cliente.precio:
        return 0
    
    cliente_max = cliente.precio
    piso_precio = piso.precio
    
    if piso_precio <= cliente_max:
        return 0  # Perfect match
    
    # Calculate percentage over client's max
    over_percentage = ((piso_precio - cliente_max) / cliente_max) * 100
    
    if over_percentage <= 10:
        return 5  # 5% penalty
    elif over_percentage <= 20:
        return 10  # 10% penalty
    else:
        return -1  # Exclude directly

def check_m2_match(piso: Piso, cliente: Cliente) -> int:
    """Check m2 match. Returns penalty (0, 5, 10) or -1 to exclude."""
    if not piso.m2 or not cliente.m2:
        return 0
    
    cliente_min = cliente.m2
    piso_m2 = piso.m2
    
    if piso_m2 >= cliente_min:
        return 0  # Perfect match
    
    # Calculate percentage under client's minimum
    under_percentage = ((cliente_min - piso_m2) / cliente_min) * 100
    
    if under_percentage <= 10:
        return 5  # 5% penalty
    elif under_percentage <= 20:
        return 10  # 10% penalty
    else:
        return -1  # Exclude directly

def check_ascensor_match(piso: Piso, cliente: Cliente) -> int:
    """Check ascensor match with floor deviation logic."""
    if not cliente.ascensor or cliente.ascensor == "INDIFERENTE":
        return 0  # No preference
    
    if not piso.ascensor:
        return 0  # No info, no penalty
    
    # Map ascensor values to floor numbers
    ascensor_floors = {
        "SÍ": 0,
        "HASTA 1º": 1,
        "HASTA 2º": 2, 
        "HASTA 3º": 3,
        "HASTA 4º": 4,
        "HASTA 5º": 5,
        "NO": 999  # Very high number for no elevator
    }
    
    cliente_floor = ascensor_floors.get(cliente.ascensor, 0)
    piso_floor = ascensor_floors.get(piso.ascensor, 0)
    
    if piso_floor <= cliente_floor:
        return 0  # Match
    
    # Calculate deviation
    deviation = piso_floor - cliente_floor
    
    if deviation == 1:
        return 5  # 5% penalty for 1 floor deviation
    elif deviation == 2:
        return 10  # 10% penalty for 2 floor deviation
    else:
        return -1  # Exclude for more than 2 floors

def check_cercania_metro_match(piso: Piso, cliente: Cliente) -> int:
    """Check metro proximity with distance deviation logic."""
    if not cliente.cercania_metro or cliente.cercania_metro == "INDIFERENTE":
        return 0  # No preference
    
    if not piso.cercania_metro:
        return 0  # No info, no penalty
    
    # Map metro distances to numeric values
    metro_distances = {
        "0-5 MIN": 1,
        "5-10 MIN": 2,
        "10-15 MIN": 3,
        "15-20 MIN": 4,
        "+20 MIN": 5,
        "INDIFERENTE": 999
    }
    
    cliente_distance = metro_distances.get(cliente.cercania_metro, 1)
    piso_distance = metro_distances.get(piso.cercania_metro, 1)
    
    if piso_distance <= cliente_distance:
        return 0  # Match (piso is closer or equal)
    
    # Calculate deviation
    deviation = piso_distance - cliente_distance
    
    if deviation == 1:
        return 5  # 5% penalty for 1 level further
    elif deviation == 2:
        return 10  # 10% penalty for 2 levels further
    else:
        return 10  # Cap at 10% penalty for metro

def check_altura_match(piso: Piso, cliente: Cliente) -> bool:
    """Check if altura matches (with flexibility)."""
    if not cliente.altura:
        return True  # No preference
    
    cliente_alturas = set(cliente.altura.split(",") if cliente.altura else [])
    piso_alturas = set(piso.altura.split(",") if piso.altura else [])
    
    if not cliente_alturas:
        return True
    if not piso_alturas:
        return False  # 5% penalty will be applied
    
    return bool(cliente_alturas.intersection(piso_alturas))

def check_interior_match(piso: Piso, cliente: Cliente) -> bool:
    """Check interior/exterior match with INDIFERENTE logic."""
    if not cliente.interior or cliente.interior == "INDIFERENTE":
        return True  # No preference
    
    if not piso.interior:
        return False  # 5% penalty will be applied
    
    # Special logic for AMBOS in piso
    if piso.interior == "AMBOS":
        return True  # AMBOS matches everything
    
    return cliente.interior == piso.interior

def check_balcon_terraza_match(piso: Piso, cliente: Cliente) -> int:
    """Check balcon and terraza match."""
    penalty = 0
    
    # Check balcon
    if cliente.balcon == "SÍ" and piso.balcon == "NO":
        penalty += 5
    
    # Check terraza  
    if cliente.terraza == "SÍ" and piso.terraza == "NO":
        penalty += 5
    
    return penalty

def check_patio_match(piso: Piso, cliente: Cliente) -> int:
    """Check patio match."""
    if cliente.patio == "SÍ" and piso.patio == "NO":
        return 5
    return 0
