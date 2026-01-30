from typing import List

from fastapi import APIRouter,HTTPException
from src.model.note import NoteCreate,NoteResponse,NoteUpdate
from src.service.note_service import create_note,get_note,get_notes,update_note,delete_notes

router=APIRouter(prefix="/notes",tags=["Notes"])

@router.post("/",response_model=dict)
async def add_note(note: NoteCreate):
    note_id=await create_note(note.model_dump())
    return {"id":note_id}

@router.get("/",response_model=List[NoteResponse])
async def list_notes():
    return await get_notes()


@router.get("/{note_id}",response_model=NoteResponse)
async def read_note(note_id:str):
    note=await get_note(note_id)
    if not note:
        raise HTTPException(status_code=404,detail="Note not found")
    return note

@router.put("/{note_id")
async def edit_note(note_id:str,note:NoteUpdate):
   updated = await update_note(note_id,note.model_dump(exclude_unset=True))
   if not updated:
       raise HTTPException(status_code=404, detail="Note not found")

   return {"message": "Note updated"}

@router.delete("/{note_id}")
async def remove_note(note_id: str):
   deleted =await delete_notes(note_id)
   if not deleted:
       raise HTTPException(status_code=404, detail="Note not found")
   return {"message": "Note deleted"}



