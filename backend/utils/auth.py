from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt

from config import db, security, security_optional, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS, FORUM_JWT_EXPIRATION_HOURS


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_token(user_id: str, email: str, is_admin: bool = False, expiration_hours: int = JWT_EXPIRATION_HOURS) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_forum_token(user_id: str, pseudo: str, is_anonymous: bool) -> str:
    payload = {
        "sub": user_id,
        "pseudo": pseudo,
        "is_anonymous": is_anonymous,
        "is_forum_user": True,
        "exp": datetime.now(timezone.utc) + timedelta(hours=FORUM_JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_client_token(client_id: str, email: str, name: str) -> str:
    payload = {
        "sub": client_id,
        "email": email,
        "name": name,
        "is_client": True,
        "exp": datetime.now(timezone.utc) + timedelta(hours=FORUM_JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        if admin_id is None or payload.get("is_forum_user"):
            raise HTTPException(status_code=401, detail="Token invalide")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

async def get_current_forum_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None or not payload.get("is_forum_user"):
            raise HTTPException(status_code=401, detail="Token invalide")
        user = await db.forum_users.find_one({"id": user_id}, {"_id": 0})
        if user and user.get("is_banned"):
            raise HTTPException(status_code=403, detail="Votre compte a été suspendu")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

async def get_optional_forum_user(credentials: HTTPAuthorizationCredentials = Depends(security_optional)):
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if not payload.get("is_forum_user"):
            return None
        return payload
    except:
        return None

async def get_current_client(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        client_id = payload.get("sub")
        if client_id is None or not payload.get("is_client"):
            raise HTTPException(status_code=401, detail="Token invalide")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")
