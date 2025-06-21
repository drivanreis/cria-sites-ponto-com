# backend/tests/integration/admin_users/test_admin_users_integration_02.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_admin_user_by_id(async_client: AsyncClient, admin_access_token, test_admin_user):
    response = await async_client.get(f"/admin-users/{test_admin_user.id}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_admin_user.id

@pytest.mark.asyncio
async def test_update_admin_user(async_client: AsyncClient, admin_access_token, test_admin_user):
    payload = {
        "email": "updated_admin@example.com"
    }
    response = await async_client.put(f"/admin-users/{test_admin_user.id}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated_admin@example.com"

@pytest.mark.asyncio
async def test_delete_admin_user(async_client: AsyncClient, admin_access_token, test_admin_user):
    response = await async_client.delete(f"/admin-users/{test_admin_user.id}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert response.status_code == 204
