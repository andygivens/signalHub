import os
import hashlib
import hmac
from typing import Optional
from passlib.context import CryptContext
from sqlmodel import select
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .db import get_session
from .models import AdminUser

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
SECRET_KEY = "supersecretkey"  # Use a secure value in production
ALGORITHM = "HS256"

def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw)

def verify_password(pw: str, hash: str) -> bool:
    return pwd_ctx.verify(pw, hash)

def bootstrap_admin():
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass = os.getenv("ADMIN_PASS")
    if not admin_pass:
        return
    with get_session() as s:
        stmt = select(AdminUser).where(AdminUser.username == admin_user)
        res = s.exec(stmt).first()
        if not res:
            user = AdminUser(username=admin_user, password_hash=hash_password(admin_pass))
            s.add(user)
            s.commit()

def check_api_key(key: str) -> Optional[AdminUser]:
    if not key:
        return None
    with get_session() as s:
        stmt = select(AdminUser)
        for u in s.exec(stmt):
            if u.api_key_hash and hmac.compare_digest(u.api_key_hash, hashlib.sha256(key.encode()).hexdigest()):
                return u
    return None

def get_current_user(token: str = Depends(oauth2_scheme)) -> AdminUser:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    with get_session() as s:
        stmt = select(AdminUser).where(AdminUser.username == username)
        user = s.exec(stmt).first()
        if user is None:
            raise credentials_exception
        return user
