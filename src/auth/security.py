from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from datetime import datetime,timezone,timedelta

pwd_context=CryptContext(schemes=["argon2"],deprecated="auto")

def hash_passwd(passwd:str):
    return pwd_context.hash(passwd)

def verify_passwd(plain_passwd,hashed_passwd):
    return pwd_context.verify(plain_passwd,hashed_passwd)

"""jwt config"""

JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY","CHANGE_ME")
JWT_ALGORITHM="HS256"

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7


"""jwt creation helpers"""
def create_access_token(user_id:str)->str:
    expire=datetime.now(timezone.utc)+timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES

    )

    payload={
        "sub":user_id,
        "type":"access",
        "exp":expire
    }

    return jwt.encode(payload,JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id:str)->str:
    expire=datetime.now(timezone.utc)+timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload={
        "sub":user_id,
        "type":"refresh",
        "exp":expire

    }

    return jwt.encode(payload,JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)




"""JWT verification"""

def decode_token(token:str)->dict:

    try:
        payload=jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise