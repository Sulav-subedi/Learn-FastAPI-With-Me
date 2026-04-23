import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from database import db_dependency
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models import User
from schemas import UserInfo

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EXPIRY_MINUTES = 30

oauth2scheme = OAuth2PasswordBearer(tokenUrl="login")

pwdcontext = CryptContext(schemes=["pbkdf2_sha256"])

def hash_password(password: str) -> str:
    return pwdcontext.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwdcontext.verify(password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRY_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(db: db_dependency, token: str = Depends(oauth2scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        db_user = db.query(User).filter(User.username == username).first()
        return UserInfo(
            id = db_user.id,
            username = db_user.username
        )
    except JWTError:   
        raise HTTPException(status_code=401, detail="Could not validate credentials")

