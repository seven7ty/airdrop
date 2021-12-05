import time
import datetime
import logging
import discord
from typing import Union, Optional
from ..db import DATABASE
from .airdrop_components import AirdropButton
from .airdrop import Airdrop
from .errors import AirdropNotFound
from .. import CONFIG

__all__: tuple = ('AirdropManager',)


class AirdropManager:
    def __init__(self, bot: discord.Bot):
        self._state: dict[int, Airdrop] = {}
        self.bot: discord.Bot = bot
        self.logger: logging.Logger = logging.getLogger('airdrops')

    async def __fetch_db_state(self) -> list[Airdrop]:
        fetched: list[Airdrop] = []
        async for doc in DATABASE.db.airdrops.find():
            fetched.append(Airdrop(guild_id=doc['gid'],
                                   channel_id=doc['cid'],
                                   message_id=doc['_id'],
                                   amount=doc['amount'],
                                   end_time=doc['end_time'],
                                   entrants=doc['entrants']))
        return fetched

    async def _add_from_message(self,
                                message: discord.Message,
                                amount: Union[int, float],
                                duration: Union[int, float],
                                channel: Optional[discord.TextChannel] = None) -> Airdrop:
        airdrop: Airdrop = Airdrop.from_message(message, amount, int(time.time()) + duration, channel)
        await DATABASE.db.airdrops.insert_one(airdrop.to_db_dict())
        self._state[airdrop.message_id] = airdrop
        return airdrop

    async def _remove(self, airdrop: Union[int, Airdrop]) -> None:
        airdrop: Airdrop = self.get_airdrop(airdrop)
        del self._state[airdrop.message_id]
        await self.bot.get_channel(airdrop.channel_id).get_partial_message(
            airdrop.message_id).unpin(reason='Airdrop cancellation')
        await DATABASE.db.airdrops.delete_one({'_id': airdrop.message_id})

    async def _fetch(self):
        self._state.update({ad.message_id: ad for ad in await self.__fetch_db_state()})

    async def update(self) -> None:
        await self._fetch()

    async def setup(self):
        await self.update()

    def get_airdrop(self, message_id: Union[int, Airdrop]) -> Airdrop:
        ad: Optional[Airdrop] = self._state.get(message_id) if not isinstance(message_id, Airdrop) else message_id
        if not ad:
            raise AirdropNotFound(f'Airdrop with message_id {message_id} not found')
        return ad

    async def new_airdrop(self,
                          ctx: discord.commands.ApplicationContext,
                          amount: Union[int, float],
                          duration: Union[int, float],
                          channel: Optional[discord.TextChannel] = None):
        channel: discord.TextChannel = channel or ctx.channel
        embed: discord.Embed = discord.Embed(title=':airplane:  An airdrop appears!',
                                             description=f'{ctx.author.mention}  left an airdrop of `{amount}{CONFIG.token_symbol}`!',
                                             color=CONFIG.token_color,
                                             timestamp=datetime.datetime.fromtimestamp(time.time() + duration))
        embed.set_footer(text=f'Ends', icon_url=ctx.bot.user.avatar.url)
        view: discord.ui.View = discord.ui.View()
        root: discord.Message = await channel.send(embed=embed, view=view)
        airdrop: Airdrop = await self._add_from_message(root, amount, duration, channel)
        view.add_item(AirdropButton(airdrop))
        await root.edit(view=view)
        await root.pin(reason='Airdrop creation')

    async def cancel(self, airdrop: Union[int, Airdrop]) -> None:
        await self._remove(airdrop)
        # notify

    async def resolve(self, airdrop: Union[int, Airdrop]) -> None:
        airdrop: Airdrop = self.get_airdrop(airdrop)
        await airdrop.resolve(self.bot)
        await self._remove(airdrop)

    async def frame(self):
        await self.update()
        to_resolve: list[Airdrop] = []
        for airdrop in self._state.values():
            if airdrop.ended and airdrop.ends_in <= 0:
                to_resolve.append(airdrop)
        for ad in to_resolve:
            self.logger.log(logging.INFO, f'Dispatching resolve operation for airdrop {ad.message_id}')
            await self.resolve(ad)
