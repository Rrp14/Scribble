from src.data import database
from src.utils.object_id import validate_object_id
from src.serializers.note_serializers import note_serializer

"""Create NOTES"""


async def create_note(note: dict):
    res = await database.db.notes.insert_one(note)
    return str(res.inserted_id)


"""Read NOTES ALL"""


async def get_notes(user_id):
    notes = []
    async for doc in database.db.notes.find({"user_id":user_id}):
        notes.append(note_serializer(doc))
    return notes


"""Read ONE"""


async def get_note(note_id: str):
    oid=validate_object_id(note_id)
    doc = await database.db.notes.find_one({"_id": oid})
    if not doc:
        return None
    return note_serializer(doc)


"""Update """


async def update_note(note_id: str, data: dict)->bool:
   oid = validate_object_id(note_id)
   result= await database.db.notes.update_one(
        {"_id": oid},
        {"$set": data}
    )
   return result.matched_count>0


"""Delete"""


async def delete_notes(note_id: str)->bool:
    oid = validate_object_id(note_id)
    result=await database.db.notes.delete_one({
        "_id": oid,
    })
    return result.deleted_count>0
