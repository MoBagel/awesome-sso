from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

from awesome_sso.service.user.schema import AwesomeUser


class MongoSettings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27000/beanie_db"
    mongodb_db_name: str = "beanie_db"


async def init_mongo():
    settings = MongoSettings()
    models = [AwesomeUser]
    cli = AsyncIOMotorClient(settings.mongodb_dsn)
    await init_beanie(
        database=cli[settings.mongodb_db_name],
        document_models=models,
    )
    for model in models:
        await model.get_motor_collection().drop()
        await model.get_motor_collection().drop_indexes()

