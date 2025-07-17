from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Compania(Base):
    __tablename__ = "companias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania")

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    telefono = Column(String)
    zona = Column(String)  # Changed to String to match Excel's named zones
    subzonas = Column(String)
    precio = Column(Float)
    tipo_vivienda = Column(String)
    finalidad = Column(String)
    habitaciones = Column(Integer)
    banos = Column(String)  # e.g., "1+1" from Excel
    estado = Column(String)
    ascensor = Column(String)
    bajos = Column(String)
    entreplanta = Column(String)
    m2 = Column(Integer)
    altura = Column(String)
    cercania_metro = Column(String)
    orientacion = Column(String)
    edificio_semi_nuevo = Column(String)
    adaptado_movilidad = Column(String)
    balcon = Column(String)
    patio = Column(String)
    terraza = Column(String)
    garaje = Column(String)
    trastero = Column(String)
    interior = Column(String)
    piscina = Column(String)
    urbanizacion = Column(String)
    vistas = Column(String)
    caracteristicas_adicionales = Column(String)
    banco = Column(String)
    ahorro = Column(Float)
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania")

class Piso(Base):
    __tablename__ = "pisos"
    id = Column(Integer, primary_key=True, index=True)
    precio = Column(Float)
    tipo_vivienda = Column(String)
    habitaciones = Column(Integer)
    banos = Column(String)
    estado = Column(String)
    ascensor = Column(String)
    bajos = Column(String)
    entreplanta = Column(String)
    m2 = Column(Integer)
    altura = Column(String)
    cercania_metro = Column(String)
    orientacion = Column(String)
    edificio_semi_nuevo = Column(String)
    adaptado_movilidad = Column(String)
    balcon = Column(String)
    patio = Column(String)
    terraza = Column(String)
    garaje = Column(String)
    trastero = Column(String)
    interior = Column(String)
    piscina = Column(String)
    urbanizacion = Column(String)
    vistas = Column(String)
    caracteristicas_adicionales = Column(String)
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania")

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
