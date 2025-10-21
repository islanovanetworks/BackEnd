import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, text
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
    fecha_caducidad_trial = Column(String, nullable=True)  # Formato: "YYYY-MM-DD" o None para sin límite
    usuarios = relationship("Usuario", back_populates="compania")
    clientes = relationship("Cliente", back_populates="compania")
    pisos = relationship("Piso", back_populates="compania")
    zonas = relationship("CompaniaZona", back_populates="compania")  # NUEVO: Relación con zonas

class CompaniaZona(Base):
    __tablename__ = "companias_zonas"
    id = Column(Integer, primary_key=True, index=True)
    compania_id = Column(Integer, ForeignKey("companias.id"))
    zona = Column(String, index=True)  # Nombre de la zona (ALTO, OLIVOS, etc.)
    compania = relationship("Compania", back_populates="zonas")

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
    paralizado = Column(String, default="NO", nullable=True)  # NUEVO: Campo para paralizar pisos
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
    
    # 🆕 MIGRACIÓN SEGURA: Añadir columna paralizado si no existe
    migrate_add_paralizado_column()
    
    # 🆕 MIGRACIÓN SEGURA: Crear tabla companias_zonas y poblar con zonas existentes
    migrate_create_zonas_table()
    migrate_add_fecha_caducidad_trial()
    

def migrate_add_paralizado_column():
    """
    🛡️ MIGRACIÓN SEGURA - Añadir columna paralizado sin afectar datos existentes
    """
    try:
        db = SessionLocal()
        
        # Verificar si la columna ya existe usando text() para SQLAlchemy 2.0
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='pisos' AND column_name='paralizado';"))
        column_exists = result.fetchone()
        
        if not column_exists:
            print("🔄 MIGRACIÓN: Añadiendo columna 'paralizado' a tabla pisos...")
            
            # Añadir columna con valor por defecto 'NO'
            db.execute(text("ALTER TABLE pisos ADD COLUMN paralizado VARCHAR DEFAULT 'NO';"))
            
            # Actualizar todos los registros existentes con 'NO' (pisos activos)
            db.execute(text("UPDATE pisos SET paralizado = 'NO' WHERE paralizado IS NULL;"))
            
            db.commit()
            print("✅ MIGRACIÓN COMPLETADA: Columna 'paralizado' añadida exitosamente")
            print("✅ Todos los pisos existentes marcados como ACTIVOS (paralizado='NO')")
        else:
            print("✅ MIGRACIÓN NO NECESARIA: Columna 'paralizado' ya existe")
            
    except Exception as e:
        print(f"❌ ERROR EN MIGRACIÓN: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()

def migrate_add_fecha_caducidad_trial():
    """
    🛡️ MIGRACIÓN SEGURA - Añadir columna fecha_caducidad_trial sin afectar datos existentes
    """
    try:
        db = SessionLocal()
        
        # Verificar si la columna ya existe
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='companias' AND column_name='fecha_caducidad_trial';"))
        column_exists = result.fetchone()
        
        if not column_exists:
            print("🔄 MIGRACIÓN: Añadiendo columna 'fecha_caducidad_trial' a tabla companias...")
            
            # Añadir columna
            db.execute(text("ALTER TABLE companias ADD COLUMN fecha_caducidad_trial VARCHAR;"))
            
            db.commit()
            print("✅ MIGRACIÓN COMPLETADA: Columna 'fecha_caducidad_trial' añadida exitosamente")
        else:
            print("✅ MIGRACIÓN NO NECESARIA: Columna 'fecha_caducidad_trial' ya existe")
            
    except Exception as e:
        print(f"❌ ERROR EN MIGRACIÓN: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()

def migrate_create_zonas_table():
    """
    🛡️ MIGRACIÓN SEGURA - Crear tabla companias_zonas y poblar con zonas existentes
    """
    try:
        db = SessionLocal()
        
        # Verificar si la tabla ya existe
        result = db.execute(text("SELECT to_regclass('companias_zonas');"))
        table_exists = result.fetchone()[0]
        
        if not table_exists:
            print("🔄 MIGRACIÓN: Creando tabla 'companias_zonas'...")
            
            # Crear la tabla usando el modelo
            Base.metadata.create_all(bind=engine)
            
            print("✅ MIGRACIÓN: Tabla 'companias_zonas' creada exitosamente")
            
            # Poblar con zonas por defecto de la primera compañía (tu oficina actual)
            print("🔄 MIGRACIÓN: Poblando zonas por defecto para compañía existente...")
            
            zonas_default = ["ALTO", "OLIVOS", "LAGUNA", "BATÁN", "SEPÚLVEDA", "MANZANARES", "PÍO", "PUERTA", "JESUITAS"]
            
            # Obtener todas las compañías existentes
            companias = db.execute(text("SELECT id FROM companias;")).fetchall()
            
            for compania in companias:
                compania_id = compania[0]
                for zona in zonas_default:
                    db.execute(text(f"INSERT INTO companias_zonas (compania_id, zona) VALUES ({compania_id}, '{zona}');"))
            
            db.commit()
            print(f"✅ MIGRACIÓN COMPLETADA: Zonas por defecto asignadas a {len(companias)} compañía(s)")
        else:
            print("✅ MIGRACIÓN NO NECESARIA: Tabla 'companias_zonas' ya existe")
            
    except Exception as e:
        print(f"❌ ERROR EN MIGRACIÓN: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()

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
