import pytest

from src.utils.object_id import validate_object_id

def test_validate_object_id():

    oid="507f1f77bcf86cd799439011"
    validated=validate_object_id(oid)

    assert str(validated)==oid

def test_invalid_object_id():
    with pytest.raises(ValueError):
        validate_object_id("not-an-object-id")