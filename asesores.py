from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from models import get_db, Usuario, Cliente
from utils import get_current_user, require_supervisor

router = APIRouter(prefix="/asesores", tags=["asesores"])

class AsesorResponse(BaseModel):
    id: int
    email: str
    rol: str
    compania_id: int
    clientes_count: int

class ClienteAsignacionRequest(BaseModel):
    cliente_id: int
    nuevo_asesor_id: int

@router.get("/", response_model=list[AsesorResponse])
def get_asesores(db: Session = Depends(get_db), current_user=Depends(require_supervisor)):
    """Solo Supervisores pueden ver la lista de asesores de su compañía"""
    asesores = db.query(Usuario).filter(Usuario.compania_id == current_user.compania_id).all()
    
    result = []
    for asesor in asesores:
        clientes_count = db.query(Cliente).filter(Cliente.asesor_id == asesor.id).count()
        result.append(AsesorResponse(
            id=asesor.id,
            email=asesor.email,
            rol=asesor.rol,
            compania_id=asesor.compania_id,
            clientes_count=clientes_count
        ))
    
    return result

@router.put("/reasignar-cliente", response_model=dict)
def reasignar_cliente(
    asignacion: ClienteAsignacionRequest, 
    db: Session = Depends(get_db), 
    current_user=Depends(require_supervisor)
):
    """Solo Supervisores pueden reasignar clientes entre asesores"""
    
    # Verificar que el cliente existe y pertenece a la compañía
    cliente = db.query(Cliente).filter(
        Cliente.id == asignacion.cliente_id,
        Cliente.compania_id == current_user.compania_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Verificar que el nuevo asesor existe y pertenece a la compañía
    nuevo_asesor = db.query(Usuario).filter(
        Usuario.id == asignacion.nuevo_asesor_id,
        Usuario.compania_id == current_user.compania_id
    ).first()
    
    if not nuevo_asesor:
        raise HTTPException(status_code=404, detail="Asesor no encontrado")
    
    # Realizar la reasignación
    cliente.asesor_id = asignacion.nuevo_asesor_id
    db.commit()
    db.refresh(cliente)
    
    return {
        "message": f"Cliente {cliente.nombre} reasignado exitosamente a {nuevo_asesor.email}",
        "cliente_id": cliente.id,
        "anterior_asesor_id": cliente.asesor_id,
        "nuevo_asesor_id": asignacion.nuevo_asesor_id
    }
