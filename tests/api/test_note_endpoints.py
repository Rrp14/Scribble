import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_note_crud_flow(async_client: AsyncClient):
    email = "apinote@testuser.com"
    password = "ValidPass@123"
    register_resp = await async_client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_resp.status_code == 200, register_resp.text
    access_token = register_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    note_payload = {"title": "API Test Note", "content": "Content from API test"}
    create_resp = await async_client.post("/notes/", json=note_payload, headers=headers)
    assert create_resp.status_code == 200, create_resp.text
    note_id = create_resp.json()["id"]
    list_resp = await async_client.get("/notes/", headers=headers)
    assert list_resp.status_code == 200, list_resp.text
    notes = list_resp.json()
    assert len(notes) == 1
    assert notes[0]["id"] == note_id
    assert notes[0]["title"] == note_payload["title"]
    read_resp = await async_client.get(f"/notes/{note_id}", headers=headers)
    assert read_resp.status_code == 200, read_resp.text
    assert read_resp.json()["content"] == note_payload["content"]
    delete_resp = await async_client.delete(f"/notes/{note_id}", headers=headers)
    assert delete_resp.status_code == 200, delete_resp.text
    assert delete_resp.json()["message"] == "Note deleted"
    empty_list_resp = await async_client.get("/notes/", headers=headers)
    assert empty_list_resp.status_code == 200, empty_list_resp.text
    assert empty_list_resp.json() == []
