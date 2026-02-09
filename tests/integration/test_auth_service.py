from typing import cast

import pytest
from pydantic import EmailStr

from src.auth.services.user_service import create_user,authenticate_user


@pytest.mark.asyncio
async def test_user_registration_and_login():
    email=cast(EmailStr, cast(object, 'integration2@test.com'))
    password="Strong@1234"

    result=await create_user(email,password)

    assert "access_token" in result
    assert "refresh_token" in result

    login=await authenticate_user(email,password)

    assert "access_token" in login

