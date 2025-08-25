from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from models import get_db, Piso
from utils import get_current_user

router = APIRouter(prefix="/pisos", tags=["pisos"])

class PisoCreate(BaseModel):
    direccion: Optional[str] = None
    zona: List[str]  # ALTO, OLIVOS, LAGUNA, BATÁN, SEPÚLVEDA, MANZANARES, PÍO, PUERTA, JESUITAS
    precio: float
    tipo_vivienda: Optional[List[str]] = None  # Piso, Casa, Chalet, Adosado, Dúplex, Ático, Estudio
    habitaciones: Optional[List[int]] = None  # 0 to 5
    estado: Optional[str] = None  # Entrar a Vivir, Actualizar, A Reformar
    ascensor: Optional[str] = None  # SÍ, HASTA 1º, HASTA 2º, HASTA 3º, HASTA 4º, HASTA 5º
    bajos: Optional[str] = None
    entreplanta: Optional[str] = None
    m2: int  # 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 150
    altura: Optional[str] = None
    cercania_metro: Optional[str] = None
    balcon_terraza: Optional[str] = None  # RENOMBRADO: Balcón/Terraza
    patio: Optional[str] = None
    interior: Optional[str] = None
    caracteristicas_adicionales: Optional[str] = None
    compania_id: int

class PisoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    direccion: Optional[str] = None
    zona: str
    precio: float
    tipo_vivienda: Optional[str]
    habitaciones: Optional[str]
    estado: Optional[str]
    ascensor: Optional[str]
    bajos: Optional[str]
    entreplanta: Optional[str]
    m2: int
    altura: Optional[str]
    cercania_metro: Optional[str]
    balcon_terraza: Optional[str]
    patio: Optional[str]
    interior: Optional[str]
    caracteristicas_adicionales: Optional[str]
    compania_id: int

@router.post("/", response_model=PisoResponse)
def create_piso(piso: PisoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if piso.compania_id != current_user.compania_id:
        raise HTTPException(status_code=403, detail="Not authorized to create piso for this compania")
    try:
        # Validaciones mejoradas
        if not piso.zona or len(piso.zona) == 0:
            raise HTTPException(status_code=400, detail="Debe seleccionar al menos una zona")
        
        if not piso.precio or piso.precio <= 0:
            raise HTTPException(status_code=400, detail="El precio debe ser mayor a 0")
            
        if not piso.m2 or piso.m2 <= 0:
            raise HTTPException(status_code=400, detail="Los metros cuadrados deben ser mayor a 0")
        
        db_piso = Piso(
            direccion=piso.direccion.strip() if piso.direccion else None,
            zona=",".join(piso.zona) if isinstance(piso.zona, list) else str(piso.zona),
            precio=float(piso.precio),
            tipo_vivienda=",".join(piso.tipo_vivienda) if piso.tipo_vivienda else None,
            habitaciones=",".join(map(str, piso.habitaciones)) if piso.habitaciones else None,
            estado=piso.estado,
            ascensor=piso.ascensor,
            bajos=piso.bajos,
            entreplanta=piso.entreplanta,
            m2=int(piso.m2),
            altura=piso.altura,
            cercania_metro=piso.cercania_metro,
            balcon_terraza=piso.balcon_terraza,
            patio=piso.patio,
            interior=piso.interior,
            caracteristicas_adicionales=piso.caracteristicas_adicionales.strip() if piso.caracteristicas_adicionales else None,
            compania_id=piso.compania_id
        )
        db.add(db_piso)
        db.commit()
        db.refresh(db_piso)
        return db_piso
    except HTTPException:
        db.rollback()
        raise
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error en los datos: {str(e)}")
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Error creating piso: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/", response_model=list[PisoResponse])
def read_pisos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    pisos = db.query(Piso).filter(Piso.compania_id == current_user.compania_id).all()
    return pisos
