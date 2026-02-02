def note_serializer(doc:dict)->dict:

    return {
        "id":str(doc["_id"]),
        "title":doc["title"],
        "content":doc["content"],
        "user_id":str(doc["user_id"])
    }