# backend/tests/integration/admin_users/test_admin_users_integration_01.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_admin_users(async_client: AsyncClient, admin_access_token):
    response = await async_client.get("/admin-users/", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_admin_user(async_client: AsyncClient, admin_access_token):
    payload = {
        "username": "newadmin",
        "email": "newadmin@example.com",
        "password": "NewAdmin123!",
        "role": "admin"
    }
    response = await async_client.post("/admin-users/", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newadmin"
    assert data["email"] == "newadmin@example.com"
