from . import CONFIG
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from lib.types import EthereumAddress
from typing import Optional

__all__: tuple = ('DATABASE',)


class _DatabaseClient(AsyncIOMotorClient):
    def __init__(self):
        self._uri: str = f'mongodb+srv://{CONFIG.env("DB_USER")}:{CONFIG.env("DB_PASS")}@{CONFIG.env("DB_HOST")}'
        super().__init__(self._uri)


class _DatabaseInterface:
    def __init__(self, client: _DatabaseClient):
        self.client: _DatabaseClient = client
        self.db: AsyncIOMotorDatabase = client[CONFIG.env('DB_NAME')]

    async def register_user(self, user_id: int, address: EthereumAddress) -> None:
        self.db.users.update_one({'_id': user_id}, {'$set': {'address': address}}, upsert=True)

    async def get_user_address(self, user_id: int) -> Optional[EthereumAddress]:
        user: Optional[dict] = await self.db.users.find_one({'_id': user_id})
        if user:
            return user['address']


DATABASE: _DatabaseInterface = _DatabaseInterface(_DatabaseClient())
