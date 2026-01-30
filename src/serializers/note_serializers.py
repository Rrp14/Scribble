def note_serializer(doc:dict)->dict:

    return {
        "id":str(doc["_id"]),
        "title":doc["title"],
        "content":doc["content"],
    }