from fastapi import APIRouter,Depends

from src.core.rate_limiter import RateLimiter
from src.auth.models.user import UserCreate, UserLogin, UserResponse, RefreshTokenRequest, LogoutRequest
from src.auth.services.user_service import create_user,authenticate_user,refresh_tokens,logout_user
from src.auth.dependecies import get_current_user

router=APIRouter(prefix="/auth",tags=["Auth"])



@router.post("/register",dependencies=[Depends(RateLimiter.from_config("AUTH_REGISTER"))])
async def register(user:UserCreate):

    res=await create_user(
        email=user.email,
        password=user.password
    )

    return res

@router.post("/login",dependencies=[Depends(RateLimiter.from_config("AUTH_LOGIN"))])
async def login(user:UserLogin):
    res=await authenticate_user(
        email=user.email,
        password=user.password
    )
    return res

@router.get("/me",response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "created_at": current_user["created_at"],
    }

@router.post("/refresh",dependencies=[Depends(RateLimiter.from_config("AUTH_REFRESH"))])
async def refresh(data:RefreshTokenRequest):
    return await refresh_tokens(data.refresh_token)


@router.post("/logout")
async def logout(data:LogoutRequest):
    return await logout_user(data.refresh_token)
