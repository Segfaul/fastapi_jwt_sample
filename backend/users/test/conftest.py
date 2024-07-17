# pylint: disable=C0413,C0114
import os

os.environ['TEST'] = 'True'

import pytest
from httpx import AsyncClient, ASGITransport

from backend.users.service.db_service import async_engine
from backend.users.config.admin import create_admin
from backend.users.main import app
from backend.users.model import Base


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ],
)
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session", autouse=True)
async def start_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def client(start_db) -> AsyncClient:
    transport = ASGITransport(
        app=app,
    )
    async with AsyncClient(
        base_url="http://127.0.0.1:8000/api/v1",
        headers={"Content-Type": "application/json"},
        transport=transport,
    ) as test_client:
        yield test_client


@pytest.fixture(scope="session")
async def admin_user(start_db):
    admin = await create_admin(username='admin', password='password')
    return admin


@pytest.fixture(scope="session")
async def admin_token(client: AsyncClient, admin_user):
    response = await client.post(
        "/auth/token", data={"username": "admin", "password": "password"},
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    assert response.status_code == 201
    token = response.json().get("access_token")
    return token
