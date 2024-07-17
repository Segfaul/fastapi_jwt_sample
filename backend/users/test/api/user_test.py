from typing import Optional

import pytest
from fastapi import status
from httpx import AsyncClient

from backend.users.util.auth_util import verify_password

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {
                "username": "dude",
                "password": "test"
            },
            status.HTTP_201_CREATED,
        ),
        (
            {
                "username": "dude",
                "password": "test"
            },
            status.HTTP_400_BAD_REQUEST,
        ),
    ),
)
async def test_add_user(
    client: AsyncClient,
    payload: dict, status_code: int
):
    response = await client.post("/user/register", json=payload)
    assert response.status_code == status_code
    if status_code == status.HTTP_201_CREATED:
        assert payload["username"] == response.json()["username"]
        assert verify_password(payload["password"], response.json()["password"])


@pytest.mark.parametrize(
    "user_id, status_code",
    (
        (
            None,
            status.HTTP_200_OK,
        ),
        (
            1,
            status.HTTP_200_OK,
        ),
        (
            10,
            status.HTTP_404_NOT_FOUND,
        ),
    ),
)
async def test_get_user(
    client: AsyncClient, admin_token: str,
    user_id: Optional[int], status_code: int
):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get(f"/user/{user_id if user_id else ''}", headers=headers)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "user_id, payload, status_code",
    (
        (
            1,
            {},
            status.HTTP_200_OK,
        ),
        (
            2,
            {
                "password": "qwerty"
            },
            status.HTTP_200_OK,
        ),
        (
            10,
            {},
            status.HTTP_404_NOT_FOUND,
        ),
    ),
)
async def test_upd_user(
    client: AsyncClient, admin_token: str,
    user_id: Optional[int], payload: dict, status_code: int
):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.patch(f"/user/{user_id}", json=payload, headers=headers)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "user_id, status_code",
    (
        (
            1,
            status.HTTP_204_NO_CONTENT,
        ),
        (
            10,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def test_delete_user(
    client: AsyncClient, admin_token: str,
    user_id: Optional[int], status_code: int
):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.delete(f"/user/{user_id}", headers=headers)
    assert response.status_code == status_code
