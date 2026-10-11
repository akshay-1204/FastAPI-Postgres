from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(payload: dict):
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=1)
    payload.update({'exp': expiry_time})
    return jwt.encode(payload, "You can't steel my app", algorithm='HS256')
