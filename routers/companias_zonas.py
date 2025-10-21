from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models import get_db, CompaniaZona, Compania
from utils import get_current_user

router = APIRouter(prefix="/companias/zonas", tags=["companias_zonas"])

class ZonaCreate(BaseModel):
    compania_id: int
    zonas: List[str]

class ZonaResponse(BaseModel):
    id: int
    compania_id: int
    zona: str

@router.get("/{compania_id}", response_model=List[ZonaResponse])
def get_zonas_by_compania(compania_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Obtener todas las zonas de una compañía específica.
    Accesible por cualquier usuario de la compañía.
    """
    # Verificar que el usuario pertenece a la compañía
    if current_user.compania_id != compania_id:
        raise HTTPException(status_code=403, detail="No autorizado para acceder a las zonas de esta compañía")
    
    zonas = db.query(CompaniaZona).filter(CompaniaZona.compania_id == compania_id).all()
    return zonas

@router.get("/", response_model=List[ZonaResponse])
def get_zonas_current_compania(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Obtener todas las zonas de la compañía del usuario actual.
    Este endpoint es el que usará el Frontend.
    """
    zonas = db.query(CompaniaZona).filter(CompaniaZona.compania_id == current_user.compania_id).all()
    
    # Si no hay zonas, retornar las zonas por defecto (para retrocompatibilidad)
    if not zonas:
        print(f"⚠️ WARNING: No hay zonas configuradas para compañía {current_user.compania_id}, usando zonas por defecto")
        zonas_default = ["ALTO", "OLIVOS", "LAGUNA", "BATÁN", "SEPÚLVEDA", "MANZANARES", "PÍO", "PUERTA", "JESUITAS"]
        return [{"id": 0, "compania_id": current_user.compania_id, "zona": zona} for zona in zonas_default]
    
    return zonas

@router.post("/", response_model=dict)
def create_zonas_for_compania(zona_data: ZonaCreate, db: Session = Depends(get_db)):
    """
    🔒 ENDPOINT ADMINISTRATIVO - Solo para administradores del sistema (TÚ)
    Crear o reemplazar zonas para una compañía.
    
    IMPORTANTE: Este endpoint NO requiere autenticación porque es para uso administrativo directo.
    En producción, deberías protegerlo con credenciales de administrador o ejecutarlo manualmente.
    """
    try:
        # Verificar que la compañía existe
        compania = db.query(Compania).filter(Compania.id == zona_data.compania_id).first()
        if not compania:
            raise HTTPException(status_code=404, detail=f"Compañía {zona_data.compania_id} no encontrada")
        
        # Eliminar zonas existentes de la compañía (para reemplazar)
        db.query(CompaniaZona).filter(CompaniaZona.compania_id == zona_data.compania_id).delete()
        
        # Crear nuevas zonas
        zonas_creadas = []
        for zona_nombre in zona_data.zonas:
            nueva_zona = CompaniaZona(
                compania_id=zona_data.compania_id,
                zona=zona_nombre.strip().upper()
            )
            db.add(nueva_zona)
            zonas_creadas.append(zona_nombre)
        
        db.commit()
        
        return {
            "message": f"Zonas actualizadas exitosamente para compañía {compania.nombre}",
            "compania_id": zona_data.compania_id,
            "compania_nombre": compania.nombre,
            "zonas_creadas": zonas_creadas,
            "total_zonas": len(zonas_creadas)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear zonas: {str(e)}")

@router.delete("/{compania_id}/{zona_id}")
def delete_zona(compania_id: int, zona_id: int, db: Session = Depends(get_db)):
    """
    🔒 ENDPOINT ADMINISTRATIVO - Eliminar una zona específica de una compañía
    """
    zona = db.query(CompaniaZona).filter(
        CompaniaZona.id == zona_id,
        CompaniaZona.compania_id == compania_id
    ).first()
    
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    
    db.delete(zona)
    db.commit()
    
    return {"message": f"Zona '{zona.zona}' eliminada exitosamente"}
