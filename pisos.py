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
    subzonas: Optional[str] = None  # NUEVO: Campo informativo
    precio: float
    tipo_vivienda: Optional[List[str]] = None  # Piso, Casa, Chalet, Adosado, Dúplex, Ático, Estudio
    habitaciones: Optional[List[int]] = None  # 0 to 5
    estado: Optional[str] = None  # Entrar a Vivir, Actualizar, A Reformar
    ascensor: Optional[str] = None  # SÍ, HASTA 1º, HASTA 2º, HASTA 3º, HASTA 4º, HASTA 5º
    bajos: Optional[str] = None
    entreplanta: Optional[str] = None
    planta: Optional[str] = None  # NUEVO: Campo informativo
    m2: int  # 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 150
    altura: Optional[str] = None
    cercania_metro: Optional[str] = None
    balcon_terraza: Optional[str] = None  # RENOMBRADO: Balcón/Terraza
    patio: Optional[str] = None
    interior: Optional[str] = None
    caracteristicas_adicionales: Optional[str] = None
    paralizado: Optional[str] = "NO"  # NUEVO: Campo para paralizar pisos
    compania_id: int

class PisoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    direccion: Optional[str] = None
    zona: str
    subzonas: Optional[str] = None  # NUEVO: Campo informativo
    precio: float
    tipo_vivienda: Optional[str]
    habitaciones: Optional[str]
    estado: Optional[str]
    ascensor: Optional[str]
    bajos: Optional[str]
    entreplanta: Optional[str]
    planta: Optional[str] = None  # NUEVO: Campo informativo
    m2: int
    altura: Optional[str]
    cercania_metro: Optional[str]
    balcon_terraza: Optional[str]
    patio: Optional[str]
    interior: Optional[str]
    caracteristicas_adicionales: Optional[str]
    paralizado: Optional[str] = "NO"  # NUEVO: Campo para paralizar pisos
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
            subzonas=piso.subzonas.strip() if piso.subzonas else None,  # NUEVO: Campo informativo
            precio=float(piso.precio),
            tipo_vivienda=",".join(piso.tipo_vivienda) if piso.tipo_vivienda else None,
            habitaciones=",".join(map(str, piso.habitaciones)) if piso.habitaciones else None,
            estado=piso.estado,
            ascensor=piso.ascensor,
            bajos=piso.bajos,
            entreplanta=piso.entreplanta,
            planta=piso.planta,  # NUEVO: Campo informativo
            m2=int(piso.m2),
            altura=piso.altura,
            cercania_metro=piso.cercania_metro,
            balcon_terraza=piso.balcon_terraza,
            patio=piso.patio,
            interior=piso.interior,
            caracteristicas_adicionales=piso.caracteristicas_adicionales.strip() if piso.caracteristicas_adicionales else None,
            paralizado=piso.paralizado or "NO",  # NUEVO: Campo para paralizar pisos
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

@router.delete("/{piso_id}")
def delete_piso(piso_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Eliminar piso - Solo Supervisores pueden eliminar pisos"""
    
    try:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        logger.info(f"Iniciando eliminación de piso {piso_id} por usuario {current_user.email}")
        
        # Verificar que es Supervisor
        if current_user.rol != "Supervisor":
            logger.error(f"Usuario {current_user.email} no es supervisor")
            raise HTTPException(status_code=403, detail="Solo supervisores pueden eliminar pisos")
        
        # Buscar el piso en la compañía del supervisor
        piso = db.query(Piso).filter(
            Piso.id == piso_id,
            Piso.compania_id == current_user.compania_id
        ).first()
        
        if not piso:
            logger.error(f"Piso {piso_id} no encontrado para compañía {current_user.compania_id}")
            raise HTTPException(status_code=404, detail="Piso no encontrado")
        
        piso_direccion = piso.direccion or f"Piso ID {piso.id}"
        logger.info(f"Piso encontrado: {piso_direccion}")
        
        # Verificar relaciones antes de eliminar
        from models import ClienteEstadoPiso
        estados_relacionados = db.query(ClienteEstadoPiso).filter(
            ClienteEstadoPiso.piso_id == piso_id
        ).all()
        
        if estados_relacionados:
            logger.info(f"Eliminando {len(estados_relacionados)} estados relacionados")
            for estado in estados_relacionados:
                db.delete(estado)
        
        # Eliminar el piso
        db.delete(piso)
        db.commit()
        
        logger.info(f"Piso {piso_direccion} eliminado exitosamente")
        return {"message": f"Piso {piso_direccion} eliminado exitosamente"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al eliminar piso {piso_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno al eliminar piso: {str(e)}")

@router.put("/{piso_id}", response_model=PisoResponse)
def update_piso(
    piso_id: int, 
    piso_data: PisoCreate, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    """Editar piso - Solo Supervisores pueden editar pisos"""
    
    # Verificar que es Supervisor
    if current_user.rol != "Supervisor":
        raise HTTPException(status_code=403, detail="Solo supervisores pueden editar pisos")
    
    # Buscar el piso en la compañía del supervisor
    piso = db.query(Piso).filter(
        Piso.id == piso_id,
        Piso.compania_id == current_user.compania_id
    ).first()
    
    if not piso:
        raise HTTPException(status_code=404, detail="Piso no encontrado")
    
    # Validar que la compañía coincida
    if piso_data.compania_id != current_user.compania_id:
        raise HTTPException(status_code=403, detail="No autorizado para esta compañía")
    
    try:
        # Validaciones
        if not piso_data.zona or len(piso_data.zona) == 0:
            raise HTTPException(status_code=400, detail="Debe seleccionar al menos una zona")
        
        if not piso_data.precio or piso_data.precio <= 0:
            raise HTTPException(status_code=400, detail="El precio debe ser mayor a 0")
            
        if not piso_data.m2 or piso_data.m2 <= 0:
            raise HTTPException(status_code=400, detail="Los metros cuadrados deben ser mayor a 0")
        
        # Actualizar campos
        # Actualizar campos
        piso.direccion = piso_data.direccion.strip() if piso_data.direccion else None
        piso.zona = ",".join(piso_data.zona) if isinstance(piso_data.zona, list) else str(piso_data.zona)
        piso.subzonas = piso_data.subzonas.strip() if piso_data.subzonas else None
        piso.precio = float(piso_data.precio)
        piso.tipo_vivienda = ",".join(piso_data.tipo_vivienda) if piso_data.tipo_vivienda else None
        piso.habitaciones = ",".join(map(str, piso_data.habitaciones)) if piso_data.habitaciones else None
        piso.estado = piso_data.estado
        piso.ascensor = piso_data.ascensor
        piso.bajos = piso_data.bajos
        piso.entreplanta = piso_data.entreplanta
        piso.planta = piso_data.planta
        piso.m2 = int(piso_data.m2)
        piso.altura = piso_data.altura
        piso.cercania_metro = piso_data.cercania_metro
        piso.balcon_terraza = piso_data.balcon_terraza
        piso.patio = piso_data.patio
        piso.interior = piso_data.interior
        piso.caracteristicas_adicionales = piso_data.caracteristicas_adicionales.strip() if piso_data.caracteristicas_adicionales else None
        piso.paralizado = piso_data.paralizado or "NO"  # NUEVO: Campo para paralizar pisos
        
        db.commit()
        db.refresh(piso)
        return piso
        
    except HTTPException:
        db.rollback()
        raise
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error en los datos: {str(e)}")
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Error updating piso: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/all", response_model=list[PisoResponse])
def read_all_pisos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Obtener todos los pisos para gestión - Solo Supervisores"""
    if current_user.rol != "Supervisor":
        raise HTTPException(status_code=403, detail="Solo supervisores pueden ver todos los pisos")
    
    pisos = db.query(Piso).filter(Piso.compania_id == current_user.compania_id).all()
    return pisos

@router.put("/{piso_id}/paralizar", response_model=PisoResponse)
def toggle_piso_paralizado(
    piso_id: int, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    """Cambiar estado de paralización de un piso - Solo Supervisores"""
    
    # Verificar que es Supervisor
    if current_user.rol != "Supervisor":
        raise HTTPException(status_code=403, detail="Solo supervisores pueden paralizar pisos")
    
    # Buscar el piso en la compañía del supervisor
    piso = db.query(Piso).filter(
        Piso.id == piso_id,
        Piso.compania_id == current_user.compania_id
    ).first()
    
    if not piso:
        raise HTTPException(status_code=404, detail="Piso no encontrado")
    
    try:
        # Cambiar estado de paralización
        piso.paralizado = "SÍ" if piso.paralizado != "SÍ" else "NO"
        
        db.commit()
        db.refresh(piso)
        
        action = "paralizado" if piso.paralizado == "SÍ" else "reactivado"
        print(f"Piso {piso.id} {action} por supervisor {current_user.email}")
        
        return piso
        
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Error toggling piso paralizado status {piso_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno al cambiar estado: {str(e)}")
