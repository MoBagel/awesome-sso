import pytest
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings, Field

from awesome_sso.service.user.schema import AwesomeUser


class TestSettings(BaseSettings):
    mongodb_dsn: str = Field(default="mongodb://localhost:27000/beanie_db", env='MONGODB_DSN')
    mongodb_db_name: str = Field(default="beanie_db", env='MONGODB_DB_NAME')
    minio_access_key: str = Field(default="minioadmin", env='MINIO_ACCESS_KEY')
    minio_secret_key: str = Field(default="minioadmin", env='MINIO_SECRET_KEY')
    minio_bucket: str = Field(default='test', env='MINIO_BUCKET')
    minio_host: str = Field(default='0.0.0.0:9000', env='MINIO_ADDRESS')


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


@pytest.fixture
async def service_name() -> str:
    return "test"


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
