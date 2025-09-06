from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from . import crud, database, models
from shared.app import schemas, settings

app = FastAPI(title="User Service")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings_obj = settings.Settings()

@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(user_credentials: schemas.UserCreate, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email=user_credentials.email)
    if not user or not pwd_context.verify(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    to_encode = {"sub": str(user.id), "exp": datetime.utcnow() + timedelta(minutes=30)}
    encoded_jwt = jwt.encode(to_encode, settings_obj.JWT_SECRET_KEY, algorithm="HS256")
    return {"access_token": encoded_jwt, "token_type": "bearer"}