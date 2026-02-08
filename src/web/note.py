from typing import List
from src.auth.dependecies import get_current_user,get_user_by_id
from fastapi import APIRouter,HTTPException,Depends
from src.model.note import NoteCreate,NoteResponse,NoteUpdate
from src.service.note_service import create_note,get_note,get_notes,update_note,delete_notes
from src.data.redis import   redis_client
import json
from src.core.sliding_rate_limiter import SlidingWindowRateLimiter

router=APIRouter(prefix="/notes",tags=["Notes"])



@router.post("/",response_model=dict,dependencies=[Depends(SlidingWindowRateLimiter.from_config("NOTES_CREATE"))])
async def add_note(note: NoteCreate ,current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    note_data=note.model_dump()
    note_data["user_id"]=current_user["_id"]

    note_id=await create_note(note_data)
    redis_client.delete(f"notes:user:{user_id}")

    return {"id":note_id}

@router.get("/",response_model=List[NoteResponse],dependencies=[Depends(SlidingWindowRateLimiter.from_config("NOTES_LIST"))])
async def list_notes(current_user=Depends(get_current_user)):
    user_id=str(current_user["_id"])
    cache_key=f"notes:user:{user_id}"

    """try cache"""
    cached=redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    """if cache miss"""
    notes= await get_notes(current_user["_id"])

    """store in redis"""
    redis_client.setex(
        cache_key,
        60,
        json.dumps(notes)
    )

    return notes




@router.get("/{note_id}",response_model=NoteResponse)
async def read_note(note_id:str,current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    cache_key=f"note:{note_id}:user:{user_id}"

    cached=redis_client.get(cache_key)
    if cached:
        return json.load(cached)



    note=await get_note(note_id)
    if not note:
        raise HTTPException(status_code=404,detail="Note not found")
    if note["user_id"]!=str(current_user["_id"]):
        raise HTTPException(403,"Forbidden")

    redis_client.setex(
        cache_key,
        60,
        json.dumps(note)
    )
    return note

@router.put("/{note_id",dependencies=[Depends(SlidingWindowRateLimiter.from_config("NOTES_UPDATE"))])
async def edit_note(note_id:str,note:NoteUpdate,current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])

    existing =await get_note(note_id)

    if not existing:
        raise HTTPException(404,"Note not Found")
    if existing["user_id"]!=str(current_user["_id"]):
        raise HTTPException(403,"Forbidden")


    await update_note(note_id,note.model_dump(exclude_unset=True))
    redis_client.delete(f"notes:user:{user_id}")

    return {"message": "Note updated"}

@router.delete("/{note_id}",dependencies=[Depends(SlidingWindowRateLimiter.from_config("NOTES_DELETE"))])
async def remove_note(note_id: str,current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])

    existing=await get_note(note_id)

    if not existing:
        raise HTTPException(404,"Note not found")

    if existing["user_id"]!=str(current_user["_id"]):
        raise HTTPException(403,"Forbidden")

    await delete_notes(note_id)
    redis_client.delete(f"notes:user:{user_id}")

    return {"message": "Note deleted"}



