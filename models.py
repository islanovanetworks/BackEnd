from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Replace with your Render PostgreSQL connection string
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@host:port/dbname"
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
    zona = Column(String)
    subzonas = Column(String)
    entrada = Column(Float)
    precio = Column(Float)
    tipo_vivienda = Column(String)
    finalidad = Column(String)
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
    banco = Column(String)
    ahorro = Column(Float)
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania", back_populates="clientes")

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
    compania = relationship("Compania", back_populates="pisos")

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
