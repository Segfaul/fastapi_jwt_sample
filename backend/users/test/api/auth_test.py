import pytest
from fastapi import status
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


@pytest.fixture(scope='module', autouse=True)
async def setup_user(client: AsyncClient):
    payload = {"username": "test", "password": "test"}
    await client.post("/user/register", json=payload)
    response = await client.post(
        "/auth/token", data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    return response.json().get("access_token")


@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {
                "username": "test",
                "password": "test"
            },
            status.HTTP_201_CREATED,
        ),
        (
            {
                "username": "dude",
                "password": "test"
            },
            status.HTTP_401_UNAUTHORIZED,
        ),
    ),
)
async def test_login(
    client: AsyncClient, setup_user: str,
    payload: dict, status_code: int
):
    response = await client.post(
        "/auth/token", data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    assert response.status_code == status_code
    if status_code == status.HTTP_201_CREATED:
        assert "access_token" in response.json().keys()
        assert "refresh_token" in response.cookies.keys()


@pytest.mark.parametrize(
    "status_code",
    (
        status.HTTP_201_CREATED,
    ),
)
async def test_refresh(
    client: AsyncClient,
    status_code: int
):
    response = await client.post("/auth/refresh")
    assert response.status_code == status_code
    if status_code == status.HTTP_201_CREATED:
        assert "access_token" in response.json().keys()


@pytest.mark.parametrize(
    "include_headers, status_code",
    (
        (
            False,
            status.HTTP_401_UNAUTHORIZED,
        ),
        (
            True,
            status.HTTP_204_NO_CONTENT,
        ),
    ),
)
async def test_logout(
    client: AsyncClient, admin_token: str,
    include_headers: bool, status_code: int
):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.post(
        "/auth/logout", headers=(headers if include_headers else None)
    )
    assert response.status_code == status_code
    if status_code == status.HTTP_204_NO_CONTENT:
        assert "refresh_token" not in response.cookies.__dict__.keys()
