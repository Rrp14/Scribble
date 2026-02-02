from datetime import datetime, timezone
from pydantic import EmailStr
from src.data import database
from src.auth.security import hash_passwd,verify_passwd,create_access_token,create_refresh_token,decode_token
from src.utils.object_id import validate_object_id

"""user queries"""

async def get_user_by_email(email:EmailStr)->dict | None:
    return await database.db.users.find_one({"email":email})

async def get_user_by_id(user_id:str)->dict|None:
    oid=validate_object_id(user_id)
    return await database.db.users.find_one({"_id":oid})


"""user creation"""

async def create_user(email:EmailStr,password:str)->dict:
    existing_user=await  get_user_by_email(email)
    if existing_user:
        raise ValueError("email already registered")

    now =datetime.now(timezone.utc)

    password_hash=hash_passwd(password)
    user_doc={
        "email":email,
        "password_hash":password_hash,
        "is_active":True,
        "created_at":now,
        "refresh_tokens":[]
    }

    result=await database.db.users.insert_one(user_doc)

    access_token =create_access_token(str(result.inserted_id))
    refresh_token=create_refresh_token(str(result.inserted_id))

    await database.db.users.update_one(
        {"_id":result.inserted_id},
        {"$push":{"refresh_tokens":refresh_token}}
    )

    return {
        "user_id": str(result.inserted_id),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


"""authentication"""

async def authenticate_user(email:EmailStr,password:str)->dict:


    user=await get_user_by_email(email)

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_passwd(password,user["password_hash"]):
        raise ValueError("Invalid email or password")

    user_id=str(user["_id"])

    access_token=create_access_token(user_id)
    refresh_token=create_refresh_token(user_id)

    await database.db.users.update_one(
        {"_id":user["_id"]},
        {"$push":{"refresh_tokens":refresh_token}}
    )

    return   {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

async def refresh_tokens(refresh_token:str)->dict:
    payload=decode_token(refresh_token)

    if payload.get("type")!="refresh":
        raise ValueError("invalid token type")

    user_id=payload.get("sub")
    user=await get_user_by_id(user_id)

    if not user:
        raise ValueError("user not found")

    tokens=user.get("refresh_tokens",[])

    if refresh_token not in tokens:
        raise ValueError("refresh token revoked")

    new_access=create_access_token(user_id)
    new_refresh=create_refresh_token(user_id)

    tokens.remove(refresh_token)
    tokens.append(new_refresh)


    await database.db.users.update_one(
        {"_id":user["_id"]},
        {
            "$set":{"refresh_tokens":tokens}
        }


    )

    return{
        "access_token":new_access,
        "refresh_token":new_refresh
    }

async def logout_user(refresh_token:str)->dict:
    payload=decode_token(refresh_token)

    if payload.get("type")!="refresh":
        raise ValueError("invalid token type")

    user_id=payload.get("sub")
    user=await get_user_by_id(user_id)

    if not user:
        raise ValueError("user not found")

    await database.db.users.update_one(
        {"_id":user["_id"]},
        {"$pull":{"refresh_tokens":refresh_token}}
    )

    return {"message":"user logged out successfully"}




