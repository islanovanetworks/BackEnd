import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models import get_db, Usuario

SECRET_KEY = os.getenv("SECRET_KEY", "your-secure-secret-key")  # Use env variable in production
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        compania_id: int = payload.get("compania_id")
        if email is None or compania_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(Usuario).filter(Usuario.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
