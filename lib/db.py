import discord
from . import CONFIG
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from lib.types import EthereumAddress
from typing import Optional

__all__: tuple = ('DATABASE', 'DatabaseInterface')


class _DatabaseClient(AsyncIOMotorClient):
    def __init__(self):
        self._uri: str = f'mongodb+srv://{CONFIG.env("DB_USER")}:{CONFIG.env("DB_PASS")}@{CONFIG.env("DB_HOST")}'
        super().__init__(self._uri)


class DatabaseInterface:
    def __init__(self, client: _DatabaseClient):
        self.client: _DatabaseClient = client
        self.db: AsyncIOMotorDatabase = client[CONFIG.env('DB_NAME')]

    async def register_user(self, user_id: int, address: EthereumAddress) -> None:
        await self.db.users.update_one({'_id': user_id}, {'$set': {'address': address}}, upsert=True)

    async def get_user_address(self, user_id: int) -> Optional[EthereumAddress]:
        user: Optional[dict] = await self.db.users.find_one({'_id': user_id})
        if user:
            return user['address']

    async def get_user_id_by_address(self, address: EthereumAddress) -> Optional[int]:
        user: Optional[dict] = await self.db.users.find_one({'address': address})
        if user:
            return user['_id']

    async def add_airdrop_entrant(self, airdrop_message_id: int, entrant_id: int) -> None:
        await self.db.airdrops.update_one({'_id': airdrop_message_id}, {'$addToSet': {'entrants': entrant_id}})

    async def remove_airdrop_entrant(self, airdrop_message_id: int, entrant_id: int) -> None:
        await self.db.airdrops.update_one({'_id': airdrop_message_id}, {'$pull': {'entrants': entrant_id}})

    async def get_role_addresses(self, role: discord.Role) -> dict[discord.Member, EthereumAddress]:
        return {m: a for m, a in zip(role.members, [await self.get_user_address(m.id) for m in role.members]) if a}


DATABASE: DatabaseInterface = DatabaseInterface(_DatabaseClient())
