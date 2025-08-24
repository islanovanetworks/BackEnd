from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
import logging
from models import get_db, Usuario

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "4a8b3f9c2e7d1a5b9c8e3f7a1b2d4e6f8c9a2b3d4e5f6a7b8c9d0e1f2a3b4c5")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("JWT token created successfully")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create JWT token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create token: {str(e)}")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for email: {form_data.username}")
        user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
        if not user:
            logger.error(f"User not found: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        if not pwd_context.verify(form_data.password, user.password):
            logger.error(f"Password verification failed for: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        access_token = create_access_token(data={
            "sub": user.email, 
            "compania_id": user.compania_id,
            "user_id": user.id,
            "rol": user.rol
        })
        logger.info(f"Login successful for: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException as e:
        logger.error(f"Login failed with HTTP error: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
