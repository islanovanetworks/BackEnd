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
    subzonas = Column(String, nullable=True)  # NUEVO: Campo informativo
    precio = Column(Float)
    tipo_vivienda = Column(String, nullable=True)
    habitaciones = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    ascensor = Column(String, nullable=True)
    bajos = Column(String, nullable=True)
    entreplanta = Column(String, nullable=True)
    planta = Column(String, nullable=True)  # NUEVO: Campo informativo
    m2 = Column(Integer)
    altura = Column(String, nullable=True)
    cercania_metro = Column(String, nullable=True)
    balcon_terraza = Column(String, nullable=True)  # RENOMBRADO: Balcón/Terraza
    patio = Column(String, nullable=True)
    interior = Column(String, nullable=True)
    caracteristicas_adicionales = Column(String, nullable=True)
    compania_id = Column(Integer, ForeignKey("companias.id"))
    compania = relationship("Compania", back_populates="pisos")

class ClienteEstadoPiso(Base):
    __tablename__ = "cliente_estado_pisos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    piso_id = Column(Integer, ForeignKey("pisos.id"))
    compania_id = Column(Integer, ForeignKey("companias.id"))  # Para filtrar por compañía
    estado = Column(String, default="Pendiente")  # Pendiente, Cita Venta Puesta, Descarta, No contesta
    fecha_actualizacion = Column(String)  # Para tracking
    
    # Relationships
    cliente = relationship("Cliente")
    piso = relationship("Piso")
    compania = relationship("Compania")

import os

def create_db_and_tables():
    """
    🛡️ MODO PRODUCCIÓN SEGURO
    - SOLO crea tablas si no existen
    - NUNCA borra datos existentes
    - Protección contra pérdida de datos
    """
    # 🔒 PROTECCIÓN ABSOLUTA - Verificar variable de entorno
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    
    if ENVIRONMENT == "production":
        print("🛡️ PRODUCTION MODE: Creating tables safely (no data loss)")
        Base.metadata.create_all(bind=engine)  # SOLO crear, NUNCA borrar
        print("✅ Database tables verified safely!")
    else:
        print("⚠️ DEVELOPMENT MODE detected - still creating safely")
        Base.metadata.create_all(bind=engine)  # SIEMPRE seguro
        print("✅ Development database ready!")

def emergency_reset_database():
    """
    🚨 FUNCIÓN DE EMERGENCIA - REQUIERE CONFIRMACIÓN MANUAL
    Esta función SOLO debe usarse en desarrollo local
    REQUIERE variable de entorno específica para ejecutarse
    """
    ALLOW_RESET = os.getenv("ALLOW_DATABASE_RESET", "false")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    
    if ENVIRONMENT == "production":
        print("🚫 RESET BLOCKED: Cannot reset database in production")
        print("🛡️ Production data is protected")
        return False
    
    if ALLOW_RESET.lower() != "true":
        print("🚫 RESET BLOCKED: ALLOW_DATABASE_RESET not set to 'true'")
        print("🛡️ Database reset requires explicit permission")
        return False
    
    print("🚨 WARNING: Resetting database in 5 seconds...")
    print("🚨 ALL DATA WILL BE LOST!")
    import time
    time.sleep(5)
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset complete!")
    return True

# 📊 FUNCIÓN DE BACKUP OPCIONAL
def create_backup_info():
    """Crear información de backup sin exportar datos sensibles"""
    try:
        db = SessionLocal()
        backup_info = {
            'timestamp': datetime.now().isoformat(),
            'companias_count': db.query(Compania).count(),
            'usuarios_count': db.query(Usuario).count(),
            'clientes_count': db.query(Cliente).count(),
            'pisos_count': db.query(Piso).count(),
            'status': 'healthy'
        }
        print(f"📊 Database status: {backup_info}")
        return backup_info
    except Exception as e:
        print(f"❌ Backup info error: {e}")
        return {'status': 'error', 'message': str(e)}
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
