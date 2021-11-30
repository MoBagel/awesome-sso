from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.client = AsyncIOMotorClient(
            host=host, port=port, username=username, password=password
        )
