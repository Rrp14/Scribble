from bson import ObjectId
from src.serializers.note_serializers import note_serializer


def test_note_serializer():
    doc={
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "title": "Test",
        "content": "Hello",
        "user_id": ObjectId("507f1f77bcf86cd799439012")
    }

    result=note_serializer(doc)

    assert result["id"] == "507f1f77bcf86cd799439011"
    assert result["user_id"] == "507f1f77bcf86cd799439012"
    assert result["title"] == "Test"