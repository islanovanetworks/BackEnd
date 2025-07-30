import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Use environment variable for database URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Compania(Base):
    __tablename__ = "companias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    usuarios = relationship("Usuario", back_populates="compania")
    clientes = relationship("Cliente", back_populates="compania")
    pisos = relationship("Piso", back_populates="compania")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania", back_populates="usuarios")

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    telefono = Column(String)
    zona = Column(String)  # Comma-separated list (e.g., "ALTO,OLIVOS")
    subzonas = Column(String, nullable=True)  # Placeholder for future subzone logic
    entrada = Column(Float)  # €10,000 increments from €10,000 to €500,000
    precio = Column(Float)  # €10,000 increments to €200,000, then €20,000
    tipo_vivienda = Column(String, nullable=True)  # Comma-separated (e.g., "Piso,Casa")
    finalidad = Column(String, nullable=True)  # Comma-separated
    habitaciones = Column(String, nullable=True)  # Comma-separated (e.g., "1,2")
    banos = Column(String, nullable=True)  # Comma-separated (e.g., "1,1+1")
    estado = Column(String, nullable=True)  # Entrar a Vivir, Actualizar, A Reformar
    ascensor = Column(String, nullable=True)  # SÍ, HASTA 1º, ..., HASTA 5º
    bajos = Column(String, nullable=True)
    entreplanta = Column(String, nullable=True)
    m2 = Column(Integer)  # 30, 40, ..., 150
    altura = Column(String, nullable=True)
    cercania_metro = Column(String, nullable=True)
    orientacion = Column(String, nullable=True)  # Comma-separated
    edificio_semi_nuevo = Column(String, nullable=True)
    adaptado_movilidad = Column(String, nullable=True)
    balcon = Column(String, nullable=True)
    patio = Column(String, nullable=True)
    terraza = Column(String, nullable=True)
    garaje = Column(String, nullable=True)
    trastero = Column(String, nullable=True)
    interior = Column(String, nullable=True)
    piscina = Column(String, nullable=True)
    urbanizacion = Column(String, nullable=True)
    vistas = Column(String, nullable=True)
    caracteristicas_adicionales = Column(String, nullable=True)
    banco = Column(String, nullable=True)
    permuta = Column(String, nullable=True)  # SÍ, NO
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania", back_populates="clientes")

class Piso(Base):
    __tablename__ = "pisos"
    id = Column(Integer, primary_key=True, index=True)
    zona = Column(String)  # Comma-separated list (e.g., "ALTO,OLIVOS")
    precio = Column(Float)
    tipo_vivienda = Column(String, nullable=True)
    habitaciones = Column(String, nullable=True)
    banos = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    ascensor = Column(String, nullable=True)
    bajos = Column(String, nullable=True)
    entreplanta = Column(String, nullable=True)
    m2 = Column(Integer)
    altura = Column(String, nullable=True)
    cercania_metro = Column(String, nullable=True)
    orientacion = Column(String, nullable=True)
    edificio_semi_nuevo = Column(String, nullable=True)
    adaptado_movilidad = Column(String, nullable=True)
    balcon = Column(String, nullable=True)
    patio = Column(String, nullable=True)
    terraza = Column(String, nullable=True)
    garaje = Column(String, nullable=True)
    trastero = Column(String, nullable=True)
    interior = Column(String, nullable=True)
    piscina = Column(String, nullable=True)
    urbanizacion = Column(String, nullable=True)
    vistas = Column(String, nullable=True)
    caracteristicas_adicionales = Column(String, nullable=True)
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania", back_populates="pisos")

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
