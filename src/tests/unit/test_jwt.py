from dotenv import load_dotenv
load_dotenv()
from src.auth.security import create_refresh_token,create_access_token,decode_token


def test_access_token_creation_and_decode():
    user_id="507f1f77bcf86cd799439011"

    token=create_access_token(user_id)
    payload=decode_token(token)

    assert payload["sub"]==user_id
    assert payload["type"]=="access"
    assert "exp" in payload


def test_refresh_token_creation_and_decode():
    user_id = "507f1f77bcf86cd799439011"


    token = create_refresh_token(user_id)

    payload = decode_token(token)

    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"
    assert "exp" in payload