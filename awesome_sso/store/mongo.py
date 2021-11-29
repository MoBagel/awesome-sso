from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine


class MongoDB:
    def __init__(
        self, host: str, port: int, username: str, password: str, database: str
    ):
        self.client = AsyncIOMotorClient(
            host=host, port=port, username=username, password=password
        )
        self.engine = AIOEngine(motor_client=self.client, database=database)
