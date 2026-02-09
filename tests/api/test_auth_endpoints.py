import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_register_login_refresh_logout(async_client: AsyncClient):
    email = "api-auth@testuser.com"
    password = "ValidPass@123"

    register_response = await async_client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 200, register_response.text
    register_data = register_response.json()
    assert register_data["user_id"]
    assert "access_token" in register_data
    assert "refresh_token" in register_data

    login_response = await async_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    assert login_data["user_id"] == register_data["user_id"]
    access_token = login_data["access_token"]

    me_response = await async_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["email"] == email

    refresh_response = await async_client.post(
        "/auth/refresh",
        json={"refresh_token": login_data["refresh_token"]},
    )
    assert refresh_response.status_code == 200, refresh_response.text
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert "refresh_token" in refresh_data

    logout_response = await async_client.post(
        "/auth/logout",
        json={"refresh_token": refresh_data["refresh_token"]},
    )
    assert logout_response.status_code == 200, logout_response.text
    assert logout_response.json()["message"] == "user logged out successfully"
