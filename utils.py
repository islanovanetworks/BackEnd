import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models import get_db, Usuario

def get_secret_key():
    service_name = os.getenv("RENDER_SERVICE_NAME", "")
    external_url = os.getenv("RENDER_EXTERNAL_URL", "")
    
    if "test" in service_name.lower() or "test" in external_url.lower():
        return "TEST_4a8b3f9c2e7d1a5b9c8e3f7a1b2d4e6f8c9a2b3d4e5f6a7b8c9d0e1f2a3b4c5"
    
    return os.getenv("SECRET_KEY", "4a8b3f9c2e7d1a5b9c8e3f7a1b2d4e6f8c9a2b3d4e5f6a7b8c9d0e1f2a3b4c5")

SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        compania_id: int = payload.get("compania_id")
        user_id: int = payload.get("user_id")
        rol: str = payload.get("rol")
        if email is None or compania_id is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(Usuario).filter(Usuario.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_supervisor(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol != "Supervisor":
        raise HTTPException(status_code=403, detail="Se requieren permisos de Supervisor")
    return current_user
