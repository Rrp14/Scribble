import pytest
from bson import ObjectId
from src.service.note_service import (
create_note,
get_note,
get_notes,
update_note,
delete_notes
)


@pytest.mark.asyncio
async def test_create_and_get_note():

    user_id=ObjectId()

    note={
        "title":"integration test",
        "content":"works with Mongo",
        "user_id":user_id
    }

    note_id=await create_note(note)

    fetched=await get_note(note_id)

    assert fetched["title"]=="integration test"
    assert fetched["user_id"]==str(user_id)


@pytest.mark.asyncio
async def test_get_notes_for_user_isolated():
    user1 = ObjectId()
    user2 = ObjectId()

    await create_note({"title": "A", "content": "1", "user_id": user1})
    await create_note({"title": "B", "content": "2", "user_id": user2})

    notes1 = await get_notes(user1)
    notes2 = await get_notes(user2)

    assert len(notes1) == 1
    assert len(notes2) == 1