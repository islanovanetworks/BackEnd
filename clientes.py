from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from models import get_db, Cliente
from utils import get_current_user

router = APIRouter(prefix="/clientes", tags=["clientes"])

class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    zona: List[str]  # ALTO, OLIVOS, LAGUNA, BATÁN, SEPÚLVEDA, MANZANARES, PÍO, PUERTA, JESUITAS
    subzonas: Optional[str] = None
    entrada: float  # €10,000 to €500,000 in €10,000 increments
    precio: float  # €10,000 to €200,000 in €10,000, then €20,000
    tipo_vivienda: Optional[List[str]] = None  # Piso, Ático, Chalet, Local
    finalidad: Optional[List[str]] = None  # Primera Vivienda, Inversión
    habitaciones: Optional[List[int]] = None  # 0 to 5
    banos: Optional[List[str]] = None  # 1, 1+1, 2
    estado: Optional[List[str]] = None  # Entrar a Vivir, Actualizar, A Reformar
    ascensor: Optional[str] = None  # SÍ, Después de 1º, Después de 2º, etc.
    bajos: Optional[str] = None
    entreplanta: Optional[str] = None
    m2: int  # metros cuadrados
    altura: Optional[List[str]] = None
    cercania_metro: Optional[str] = None
    orientacion: Optional[List[str]] = None  # Norte, Sur, Este, Oeste
    edificio_semi_nuevo: Optional[str] = None
    adaptado_movilidad: Optional[str] = None
    balcon: Optional[str] = None
    patio: Optional[str] = None
    terraza: Optional[str] = None
    garaje: Optional[str] = None
    trastero: Optional[str] = None
    interior: Optional[str] = None
    piscina: Optional[str] = None
    urbanizacion: Optional[str] = None
    vistas: Optional[str] = None
    caracteristicas_adicionales: Optional[str] = None
    banco: Optional[str] = None
    permuta: Optional[str] = None  # SÍ, NO
    kiron: Optional[str] = None  # SK, PK, NK
    compania_id: int
    asesor_id: Optional[int] = None  # NUEVO: Para que Supervisor pueda asignar cliente a otro asesor

class ClienteResponse(BaseModel):
    id: int
    nombre: str
    telefono: str
    zona: str
    subzonas: Optional[str]
    entrada: float
    precio: float
    tipo_vivienda: Optional[str]
    finalidad: Optional[str]
    habitaciones: Optional[str]
    banos: Optional[str]
    estado: Optional[str]
    ascensor: Optional[str]
    bajos: Optional[str]
    entreplanta: Optional[str]
    m2: int
    altura: Optional[str]
    cercania_metro: Optional[str]
    orientacion: Optional[str]
    edificio_semi_nuevo: Optional[str]
    adaptado_movilidad: Optional[str]
    balcon: Optional[str]
    patio: Optional[str]
    terraza: Optional[str]
    garaje: Optional[str]
    trastero: Optional[str]
    interior: Optional[str]
    piscina: Optional[str]
    urbanizacion: Optional[str]
    vistas: Optional[str]
    caracteristicas_adicionales: Optional[str]
    banco: Optional[str]
    permuta: Optional[str]
    kiron: Optional[str]
    compania_id: int
    asesor_id: Optional[int]  # NUEVO
    asesor_asignado: Optional[dict] = None  # NUEVO: Para mostrar info del asesor

    class Config:
        orm_mode = True

@router.post("/", response_model=ClienteResponse)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if cliente.compania_id != current_user.compania_id:
        raise HTTPException(status_code=403, detail="Not authorized to create cliente for this compania")
    
    # Determinar el asesor asignado
    asesor_id = cliente.asesor_id
    
    # Si es Asesor, solo puede asignarse clientes a sí mismo
    if current_user.rol == "Asesor":
        asesor_id = current_user.id
    # Si es Supervisor y no especifica asesor_id, se asigna a sí mismo
    elif current_user.rol == "Supervisor" and not asesor_id:
        asesor_id = current_user.id
    # Si es Supervisor y especifica asesor_id, validar que el asesor existe y pertenece a la compañía
    elif current_user.rol == "Supervisor" and asesor_id:
        asesor_target = db.query(Usuario).filter(
            Usuario.id == asesor_id, 
            Usuario.compania_id == current_user.compania_id
        ).first()
        if not asesor_target:
            raise HTTPException(status_code=400, detail="El asesor especificado no existe o no pertenece a tu compañía")
    
    try:
        db_cliente = Cliente(
            nombre=cliente.nombre,
            telefono=cliente.telefono,
            zona=",".join(cliente.zona),
            subzonas=cliente.subzonas,
            entrada=cliente.entrada,
            precio=cliente.precio,
            tipo_vivienda=",".join(cliente.tipo_vivienda) if cliente.tipo_vivienda else None,
            finalidad=",".join(cliente.finalidad) if cliente.finalidad else None,
            habitaciones=",".join(map(str, cliente.habitaciones)) if cliente.habitaciones else None,
            banos=",".join(cliente.banos) if cliente.banos else None,
            estado=",".join(cliente.estado) if cliente.estado else None,
            ascensor=cliente.ascensor,
            bajos=cliente.bajos,
            entreplanta=cliente.entreplanta,
            m2=cliente.m2,
            altura=",".join(cliente.altura) if cliente.altura else None,
            cercania_metro=cliente.cercania_metro,
            orientacion=",".join(cliente.orientacion) if cliente.orientacion else None,
            edificio_semi_nuevo=cliente.edificio_semi_nuevo,
            adaptado_movilidad=cliente.adaptado_movilidad,
            balcon=cliente.balcon,
            patio=cliente.patio,
            terraza=cliente.terraza,
            garaje=cliente.garaje,
            trastero=cliente.trastero,
            interior=cliente.interior,
            piscina=cliente.piscina,
            urbanizacion=cliente.urbanizacion,
            vistas=cliente.vistas,
            caracteristicas_adicionales=cliente.caracteristicas_adicionales,
            banco=cliente.banco,
            permuta=cliente.permuta,
            kiron=cliente.kiron,
            compania_id=cliente.compania_id,
            asesor_id=asesor_id  # NUEVO: Asignar cliente al asesor
        )
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating cliente: {str(e)}")

@router.get("/", response_model=list[ClienteResponse])
def read_clientes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Si es Asesor, solo ve sus clientes
    if current_user.rol == "Asesor":
        clientes = db.query(Cliente).filter(
            Cliente.compania_id == current_user.compania_id,
            Cliente.asesor_id == current_user.id
        ).all()
    # Si es Supervisor, ve todos los clientes de la compañía
    else:
        clientes = db.query(Cliente).filter(Cliente.compania_id == current_user.compania_id).all()
    
    # Agregar información del asesor asignado
    for cliente in clientes:
        if cliente.asesor_asignado:
            cliente.asesor_asignado = {
                "id": cliente.asesor_asignado.id,
                "email": cliente.asesor_asignado.email,
                "rol": cliente.asesor_asignado.rol
            }
    
    return clientes


@router.delete("/{cliente_id}")
def delete_cliente(cliente_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Eliminar cliente - Asesor solo puede eliminar sus clientes, Supervisor puede eliminar cualquiera"""
    
    if current_user.rol == "Asesor":
        cliente = db.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.compania_id == current_user.compania_id,
            Cliente.asesor_id == current_user.id
        ).first()
    else:  # Supervisor
        cliente = db.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.compania_id == current_user.compania_id
        ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o sin permisos")
    
    db.delete(cliente)
    db.commit()
    return {"message": f"Cliente {cliente.nombre} eliminado exitosamente"}

@router.put("/{cliente_id}", response_model=ClienteResponse)
def update_cliente(
    cliente_id: int, 
    cliente_data: ClienteCreate, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    """Editar cliente - Asesor solo puede editar sus clientes, Supervisor puede editar cualquiera"""
    
    if current_user.rol == "Asesor":
        cliente = db.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.compania_id == current_user.compania_id,
            Cliente.asesor_id == current_user.id
        ).first()
        # Asesor no puede cambiar la asignación
        asesor_id = current_user.id
    else:  # Supervisor
        cliente = db.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.compania_id == current_user.compania_id
        ).first()
        # Supervisor puede cambiar asignación o mantener la actual
        asesor_id = cliente_data.asesor_id if cliente_data.asesor_id else cliente.asesor_id
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o sin permisos")
    
    # Validar que la compañía coincida
    if cliente_data.compania_id != current_user.compania_id:
        raise HTTPException(status_code=403, detail="No autorizado para esta compañía")
    
    # Si es Supervisor y quiere cambiar asesor, validar que el nuevo asesor existe
    if current_user.rol == "Supervisor" and asesor_id != cliente.asesor_id:
        nuevo_asesor = db.query(Usuario).filter(
            Usuario.id == asesor_id,
            Usuario.compania_id == current_user.compania_id
        ).first()
        if not nuevo_asesor:
            raise HTTPException(status_code=400, detail="El asesor especificado no existe")
    
    # Actualizar campos
    cliente.nombre = cliente_data.nombre
    cliente.telefono = cliente_data.telefono
    cliente.zona = ",".join(cliente_data.zona)
    cliente.subzonas = cliente_data.subzonas
    cliente.entrada = cliente_data.entrada
    cliente.precio = cliente_data.precio
    cliente.tipo_vivienda = ",".join(cliente_data.tipo_vivienda) if cliente_data.tipo_vivienda else None
    cliente.finalidad = ",".join(cliente_data.finalidad) if cliente_data.finalidad else None
    cliente.habitaciones = ",".join(map(str, cliente_data.habitaciones)) if cliente_data.habitaciones else None
    cliente.banos = ",".join(cliente_data.banos) if cliente_data.banos else None
    cliente.estado = ",".join(cliente_data.estado) if cliente_data.estado else None
    cliente.ascensor = cliente_data.ascensor
    cliente.bajos = cliente_data.bajos
    cliente.entreplanta = cliente_data.entreplanta
    cliente.m2 = cliente_data.m2
    cliente.altura = ",".join(cliente_data.altura) if cliente_data.altura else None
    cliente.cercania_metro = cliente_data.cercania_metro
    cliente.orientacion = ",".join(cliente_data.orientacion) if cliente_data.orientacion else None
    cliente.edificio_semi_nuevo = cliente_data.edificio_semi_nuevo
    cliente.adaptado_movilidad = cliente_data.adaptado_movilidad
    cliente.balcon = cliente_data.balcon
    cliente.patio = cliente_data.patio
    cliente.terraza = cliente_data.terraza
    cliente.garaje = cliente_data.garaje
    cliente.trastero = cliente_data.trastero
    cliente.interior = cliente_data.interior
    cliente.piscina = cliente_data.piscina
    cliente.urbanizacion = cliente_data.urbanizacion
    cliente.vistas = cliente_data.vistas
    cliente.caracteristicas_adicionales = cliente_data.caracteristicas_adicionales
    cliente.banco = cliente_data.banco
    cliente.permuta = cliente_data.permuta
    cliente.kiron = cliente_data.kiron
    cliente.asesor_id = asesor_id
    
    db.commit()
    db.refresh(cliente)
    return cliente
