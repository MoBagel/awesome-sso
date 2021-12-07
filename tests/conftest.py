import motor.motor_asyncio
import pytest
from beanie import init_beanie
from pydantic import BaseSettings

from awesome_sso.user.schema import AwesomeUser


class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27000/beanie_db"
    mongodb_db_name: str = "beanie_db"


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture()
def cli(settings, loop):
    return motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)


@pytest.fixture()
def db(cli, settings, loop):
    return cli[settings.mongodb_db_name]


@pytest.fixture(autouse=True)
async def init(loop, db):
    models = [AwesomeUser]
    await init_beanie(
        database=db,
        document_models=models,
    )
    yield None

    for model in models:
        await model.get_motor_collection().drop()
        await model.get_motor_collection().drop_indexes()
