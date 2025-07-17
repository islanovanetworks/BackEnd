from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from models import get_db, Usuario, Compania
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

@router.post("/", response_model=UserCreate)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
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
        
        # Create new user
        db_user = Usuario(
            email=user.email,
            password=hashed_password,
            compania_id=user.compania_id
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User {user.email} registered successfully with compania_id: {user.compania_id}")
        
        return user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to register user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")
