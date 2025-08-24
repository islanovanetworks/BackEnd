from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from models import get_db, Usuario, Compania
from utils import require_supervisor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/register", tags=["register"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: str
    password: str
    compania_id: int

class SupervisorUserCreate(BaseModel):
    email: str
    password: str
    compania_id: int
    rol: str = "Supervisor"

@router.post("/", response_model=UserCreate)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registro público - SOLO puede crear Asesores"""
    try:
        # Check if company exists
        compania = db.query(Compania).filter(Compania.id == user.compania_id).first()
        if not compania:
            logger.error(f"Company with ID {user.compania_id} not found")
            raise HTTPException(status_code=400, detail=f"Company with ID {user.compania_id} does not exist")
        
        # Check if email is already registered
        existing_user = db.query(Usuario).filter(Usuario.email == user.email).first()
        if existing_user:
            logger.error(f"Email {user.email} already registered")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password
        hashed_password = pwd_context.hash(user.password)
        logger.info(f"Password hashed successfully for email: {user.email}")
        
        # Create new user - SIEMPRE como Asesor
        db_user = Usuario(
            email=user.email,
            password=hashed_password,
            compania_id=user.compania_id,
            rol="Asesor"  # ✅ FORZADO - Solo Asesores
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User {user.email} registered successfully as Asesor with compania_id: {user.compania_id}")
        
        return user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to register user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

@router.post("/supervisor", response_model=SupervisorUserCreate)
def register_supervisor(
    user: SupervisorUserCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_supervisor)  # ✅ SOLO Supervisores pueden crear Supervisores
):
    """Registro de Supervisor - SOLO otro Supervisor puede crear uno"""
    try:
        # Check if company exists
        compania = db.query(Compania).filter(Compania.id == user.compania_id).first()
        if not compania:
            raise HTTPException(status_code=400, detail=f"Company with ID {user.compania_id} does not exist")
        
        # Verificar que el supervisor actual pertenece a la misma compañía
        if current_user.compania_id != user.compania_id:
            raise HTTPException(status_code=403, detail="No puedes crear supervisores en otras compañías")
        
        # Check if email is already registered
        existing_user = db.query(Usuario).filter(Usuario.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password
        hashed_password = pwd_context.hash(user.password)
        
        # Create new supervisor
        db_user = Usuario(
            email=user.email,
            password=hashed_password,
            compania_id=user.compania_id,
            rol="Supervisor"  # ✅ Supervisor creado por otro Supervisor
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Supervisor {user.email} created by {current_user.email}")
        
        return user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to register supervisor: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register supervisor: {str(e)}")
