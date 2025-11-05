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
    # Solo mostrar pisos ACTIVOS (no paralizados) para búsquedas
    pisos = db.query(Piso).filter(
        Piso.compania_id == current_user.compania_id,
        Piso.paralizado != "SÍ"
    ).all()
    return pisos

@router.delete("/{piso_id}")
def delete_piso(piso_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Eliminar piso - Supervisores y Asesores pueden eliminar pisos"""
    
    try:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        logger.info(f"Iniciando eliminación de piso {piso_id} por usuario {current_user.email} (Rol: {current_user.rol})")
        
        # Buscar el piso en la compañía del usuario
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
        
        logger.info(f"Piso {piso_direccion} eliminado exitosamente por {current_user.rol}")
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
    """Editar piso - Supervisores y Asesores pueden editar pisos"""
    
    # Buscar el piso en la compañía del usuario
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
        # Actualizar campos del piso
        piso.direccion = piso_data.direccion
        piso.zona = piso_data.zona
        piso.subzonas = piso_data.subzonas
        piso.precio = piso_data.precio
        piso.tipo_vivienda = piso_data.tipo_vivienda
        piso.habitaciones = piso_data.habitaciones
        piso.m2 = piso_data.m2
        piso.planta = piso_data.planta
        piso.ascensor = piso_data.ascensor
        piso.terraza = piso_data.terraza
        piso.garaje = piso_data.garaje
        piso.trastero = piso_data.trastero
        piso.estado_conservacion = piso_data.estado_conservacion
        piso.piscina = piso_data.piscina
        piso.amueblado = piso_data.amueblado
        piso.kiron = piso_data.kiron
        piso.permuta = piso_data.permuta
        piso.paralizado = piso_data.paralizado
        
        db.commit()
        db.refresh(piso)
        
        import logging
        logging.info(f"Piso {piso_id} actualizado exitosamente por {current_user.rol} ({current_user.email})")
        
        return piso
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
    """Obtener todos los pisos para gestión - Supervisores y Asesores"""
    
    pisos = db.query(Piso).filter(Piso.compania_id == current_user.compania_id).all()
    return pisos

@router.put("/{piso_id}/paralizar", response_model=PisoResponse)
def toggle_piso_paralizado(
    piso_id: int, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    """Cambiar estado de paralización de un piso - Supervisores y Asesores"""
    
    # Buscar el piso en la compañía del usuario
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
        print(f"Piso {piso.id} {action} por {current_user.rol} ({current_user.email})")
        
        return piso
        
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Error toggling piso paralizado status {piso_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno al cambiar estado: {str(e)}")
