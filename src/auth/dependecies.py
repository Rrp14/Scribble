from fastapi import Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from jose import JWTError
from src.auth.security import decode_token
from src.auth.services.user_service import get_user_by_id

security=HTTPBearer()


async def get_current_user(
        credentials:HTTPAuthorizationCredentials=Depends(security),

):
    token=credentials.credentials

    try:
        payload=decode_token(token)
    except JWTError:
        raise ValueError("invalid or expired token")

    if payload.get("type")!="access":
        raise ValueError("invalid token type")

    user_id=payload.get("sub")
    if not user_id:
        raise ValueError("invalid token payload")

    user =await get_user_by_id(user_id)
    if not user:
        raise ValueError("user not found")

    return user