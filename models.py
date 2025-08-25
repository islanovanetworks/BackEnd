import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

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
    rol = Column(String, default="Asesor")  # "Asesor" o "Supervisor"
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania", back_populates="usuarios")
    clientes_asignados = relationship("Cliente", back_populates="asesor_asignado")

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    telefono = Column(String)
    zona = Column(String)  # Comma-separated (e.g., "ALTO,OLIVOS")
    subzonas = Column(String, nullable=True)
    entrada = Column(Float)
    precio = Column(Float)
    tipo_vivienda = Column(String, nullable=True)  # Comma-separated
    finalidad = Column(String, nullable=True)  # Comma-separated
    habitaciones = Column(String, nullable=True)  # Comma-separated (0-5)
    estado = Column(String, nullable=True)  # Comma-separated: Entrar a Vivir, Actualizar, A Reformar
    ascensor = Column(String, nullable=True)  # SÍ, HASTA 1º, ..., HASTA 5º
    bajos = Column(String, nullable=True)
    entreplanta = Column(String, nullable=True)
    m2 = Column(Integer)  # 30, 40, ..., 150
    altura = Column(String, nullable=True)
    cercania_metro = Column(String, nullable=True)
    balcon_terraza = Column(String, nullable=True)  # RENOMBRADO: Balcón/Terraza
    patio = Column(String, nullable=True)
    interior = Column(String, nullable=True)
    caracteristicas_adicionales = Column(String, nullable=True)
    banco = Column(String, nullable=True)
    permuta = Column(String, nullable=True)  # SÍ, NO
    kiron = Column(String, nullable=True)  # SK, PK, NK
    compania_id = Column(Integer, ForeignKey("companias.id"))
    asesor_id = Column(Integer, ForeignKey("usuarios.id"))  # NUEVO: Asignación a asesor
    compania = relationship("Compania", back_populates="clientes")
    asesor_asignado = relationship("Usuario", back_populates="clientes_asignados")  # NUEVO

class Piso(Base):
    __tablename__ = "pisos"
    id = Column(Integer, primary_key=True, index=True)
    direccion = Column(String, nullable=True)
    zona = Column(String)  # Comma-separated (e.g., "ALTO,OLIVOS")
    precio = Column(Float)
    tipo_vivienda = Column(String, nullable=True)
    habitaciones = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    ascensor = Column(String, nullable=True)
    bajos = Column(String, nullable=True)
    entreplanta = Column(String, nullable=True)
    m2 = Column(Integer)
    altura = Column(String, nullable=True)
    cercania_metro = Column(String, nullable=True)
    balcon_terraza = Column(String, nullable=True)  # RENOMBRADO: Balcón/Terraza
    patio = Column(String, nullable=True)
    interior = Column(String, nullable=True)
    caracteristicas_adicionales = Column(String, nullable=True)
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania", back_populates="pisos")

def create_db_and_tables():
    # ✅ FORZAR RECREACIÓN DE TABLAS
    print("🔄 Recreating database tables...")
    Base.metadata.drop_all(bind=engine)  # Eliminar tablas existentes
    Base.metadata.create_all(bind=engine)  # Recrear todas las tablas
    print("✅ Database tables recreated successfully!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
