from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from models import get_db, Usuario, Compania

router = APIRouter(prefix="/register", tags=["register"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: str
    password: str
    compania_id: int

@router.post("/", response_model=UserCreate)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if company exists
    compania = db.query(Compania).filter(Compania.id == user.compania_id).first()
    if not compania:
        raise HTTPException(status_code=400, detail="Company does not exist")
    
    # Check if email is already registered
    existing_user = db.query(Usuario).filter(Usuario.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    
    # Create new user
    db_user = Usuario(
        email=user.email,
        password=hashed_password,
        compania_id=user.compania_id
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")
    
    return user
