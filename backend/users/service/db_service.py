import os
from typing import AsyncIterator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

env = os.environ.get
load_dotenv('./.env')

TEST = env('TEST').lower() == "true"
DEBUG = env('DEBUG').lower() == "true"
DEBUG = True
POSTGRE_CON = (
    f"postgresql+asyncpg://{env('POSTGRES_USER')}:{env('POSTGRES_PASSWORD')}"
    f"@{env('POSTGRES_HOST')}:{env('POSTGRES_PORT')}/{env('POSTGRES_DB')}"
)
ENGINE_PARAMS = {
    'url': f'sqlite+aiosqlite:///{"test_users" if TEST else "users"}.db'
    if (DEBUG or TEST) else POSTGRE_CON,
    'pool_pre_ping': True,
    'echo': False
}
SESSION_PARAMS = {
    'autoflush': False,
    'expire_on_commit': False,
    'future': True
}

# API engine settings (default poolclass to maintain pool of db connections)
async_engine = create_async_engine(
    **ENGINE_PARAMS
)
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    **SESSION_PARAMS
)


async def get_session() -> AsyncIterator[async_sessionmaker]:
    async with AsyncSessionFactory() as session:
        yield session
