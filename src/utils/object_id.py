from bson import ObjectId
from bson.errors import InvalidId

def validate_object_id(id_str:str)->ObjectId:

    try:
        return ObjectId(id_str)
    except InvalidId:
        raise ValueError("invalid Object id format")