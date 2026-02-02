from typing import List
from src.auth.dependecies import get_current_user,get_user_by_id
from fastapi import APIRouter,HTTPException,Depends
from src.model.note import NoteCreate,NoteResponse,NoteUpdate
from src.service.note_service import create_note,get_note,get_notes,update_note,delete_notes

router=APIRouter(prefix="/notes",tags=["Notes"])

@router.post("/",response_model=dict)
async def add_note(note: NoteCreate ,current_user=Depends(get_current_user)):
    note_data=note.model_dump()
    note_data["user_id"]=current_user["_id"]

    note_id=await create_note(note_data)
    return {"id":note_id}

@router.get("/",response_model=List[NoteResponse])
async def list_notes(current_user=Depends(get_current_user)):
    return await get_notes(current_user["_id"])


@router.get("/{note_id}",response_model=NoteResponse)
async def read_note(note_id:str,current_user=Depends(get_current_user)):
    note=await get_note(note_id)
    if not note:
        raise HTTPException(status_code=404,detail="Note not found")
    if note["user_id"]!=str(current_user["_id"]):
        raise HTTPException(403,"Forbidden")
    return note

@router.put("/{note_id")
async def edit_note(note_id:str,note:NoteUpdate,current_user=Depends(get_current_user)):

    existing =await get_note(note_id)

    if not existing:
        raise HTTPException(404,"Note not Found")
    if existing["user_id"]!=str(current_user["_id"]):
        raise HTTPException(403,"Forbidden")


    await update_note(note_id,note.model_dump(exclude_unset=True))


    return {"message": "Note updated"}

@router.delete("/{note_id}")
async def remove_note(note_id: str,current_user=Depends(get_current_user)):

    existing=await get_note(note_id)

    if not existing:
        raise HTTPException(404,"Note not found")

    if existing["user_id"]!=str(current_user["_id"]):
        raise HTTPException(403,"Forbidden")

    await delete_notes(note_id)

    return {"message": "Note deleted"}



