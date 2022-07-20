import pytest
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings, Field

from awesome_sso.service.user.schema import AwesomeUser


class TestSettings(BaseSettings):
    mongodb_dsn: str = Field(
        default="mongodb://localhost:27017/beanie_db", env="MONGODB_DNS"
    )
    mongodb_db_name: str = Field(default="beanie_db", env="MONGODB_DB_NAME")


@pytest.fixture
def settings():
    return TestSettings()


@pytest.fixture
async def public_key() -> str:
    return open("tests/key_pairs/test.key.pub").read()


@pytest.fixture
async def private_key() -> str:
    return open("tests/key_pairs/test.key").read()


@pytest.fixture
async def symmetric_key() -> str:
    return "chloeisboss"


@pytest.fixture
async def symmetric_algorithm() -> str:
    return "HS256"


@pytest.fixture
async def asymmetric_algorithm() -> str:
    return "RS256"


async def init_mongo():
    settings = TestSettings()
    models = [AwesomeUser]
    cli = AsyncIOMotorClient(settings.mongodb_dsn)
    await init_beanie(
        database=cli[settings.mongodb_db_name],
        document_models=models,
    )
    for model in models:
        await model.get_motor_collection().drop()
        await model.get_motor_collection().drop_indexes()
