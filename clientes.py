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
    tipo_vivienda: Optional[List[str]] = None  # Piso, Casa, Chalet, Adosado, Dúplex, Ático, Estudio
    finalidad: Optional[List[str]] = None  # Primera Vivienda, Inversión
    habitaciones: Optional[List[int]] = None  # 0 to 5
    banos: Optional[List[str]] = None  # 1, 1+1, 2
    estado: Optional[List[str]] = None  # ✅ CAMBIADO: Entrar a Vivir, Actualizar, A Reformar - AHORA ACEPTA MÚLTIPLES
    ascensor: Optional[str] = None  # SÍ, HASTA 1º, HASTA 2º, HASTA 3º, HASTA 4º, HASTA 5º
    bajos: Optional[str] = None
    entreplanta: Optional[str] = None
    m2: int  # 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 150
    altura: Optional[str] = None
    cercania_metro: Optional[str] = None
    orientacion: Optional[List[str]] = None  # Norte, Sur, Este, Oeste, Indiferente
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
    compania_id: int

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
    estado: Optional[str]  # Se almacena como string separado por comas
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
    compania_id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=ClienteResponse)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if cliente.compania_id != current_user.compania_id:
        raise HTTPException(status_code=403, detail="Not authorized to create cliente for this compania")
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
        estado=",".join(cliente.estado) if cliente.estado else None,  # ✅ CAMBIADO: Ahora maneja arrays
        ascensor=cliente.ascensor,
        bajos=cliente.bajos,
        entreplanta=cliente.entreplanta,
        m2=cliente.m2,
        altura=cliente.altura,
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
        compania_id=cliente.compania_id
    )
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.get("/", response_model=list[ClienteResponse])
def read_clientes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    clientes = db.query(Cliente).filter(Cliente.compania_id == current_user.compania_id).all()
    return clientes
