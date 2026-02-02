from pydantic import BaseModel,Field

class NoteCreate(BaseModel):
    title:str =Field(min_length=1,max_length=50)
    content:str =Field(min_length=0,max_length=10000)

class NoteUpdate(BaseModel):
    title:str | None
    content:str | None

class NoteResponse(BaseModel):
    id:str
    title:str
    content:str
    user_id:str
