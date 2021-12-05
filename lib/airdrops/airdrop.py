import asyncio
import discord
import logging
import datetime
import time
from typing import Union, Optional, Iterable
from .. import DATABASE, CRYPTO, CONFIG
from ..types import EthereumAddress, TxHash

__all__: tuple = ('Airdrop',)
logger: logging.Logger = logging.getLogger('airdrops')


class Airdrop:
    __slots__: tuple = ('channel_id', 'guild_id', 'message_id', 'amount', 'entrants', 'resolve_params', 'end_time')

    def __init__(self,
                 guild_id: int,
                 channel_id: int,
                 message_id: int,
                 amount: Union[int, float],
                 end_time: int,
                 entrants: Optional[Iterable[int]] = None):
        self.channel_id: int = channel_id
        self.guild_id: int = guild_id
        self.message_id: int = message_id
        self.amount: Union[int, float] = amount
        self.entrants = set(entrants) if entrants else set()
        self.end_time: int = end_time

    @property
    def url(self) -> str:
        return f'https://discord.com/channels/{self.guild_id}/{self.channel_id}/{self.message_id}'

    @property
    def ended(self) -> bool:
        return self.ends_in <= 0

    @property
    def ends_in(self) -> int:
        return self.end_time - int(round(time.time()))

    @property
    def is_expired(self) -> bool:
        return self.ends_in <= 60*60*3

    @property
    def split(self) -> float:
        return self.amount / len(self.entrants) if self.entrants else 0

    def to_db_dict(self) -> dict[str, Union[int, list[int], float]]:
        return {
            '_id': self.message_id,
            'gid': self.guild_id,
            'cid': self.channel_id,
            'amount': self.amount,
            'end_time': self.end_time,
            'entrants': list(self.entrants)
        }

    @classmethod
    def from_message(cls,
                     message: discord.Message,
                     amount: Union[int, float],
                     end_time: int,
                     channel: Optional[discord.TextChannel] = None) -> 'Airdrop':
        return cls(
            guild_id=message.guild.id,
            channel_id=channel.id if channel else message.channel.id,
            message_id=message.id,
            amount=amount,
            end_time=end_time
        )

    async def add_entrant(self, user: Union[discord.User, int]) -> None:
        id_: int = user.id if not isinstance(user, int) else user
        self.entrants.add(id_)
        await DATABASE.add_airdrop_entrant(self.message_id, id_)

    async def remove_entrant(self, user: Union[discord.User, int]) -> None:
        id_: int = user.id if not isinstance(user, int) else user
        self.entrants.remove(id_)
        await DATABASE.remove_airdrop_entrant(self.message_id, id_)

    async def join(self, interaction: discord.Interaction) -> None:
        if interaction.user.id not in self.entrants:
            if not await DATABASE.get_user_address(interaction.user.id):
                await interaction.response.send_message('**You don\'t have an ETH address associated!**'
                                                        ' Use the `/register` command to do so.', ephemeral=True)
                return
            await self.add_entrant(interaction.user)
            embed: discord.Embed = discord.Embed(
                title=':rocket:  Welcome aboard!',
                description=f'You have joined the airdrop!\n'
                            f'The reward will be **split evenly between all entrants.**\n',
                color=discord.Color.green()
            )
            embed.set_footer(text='When this airdrop ends and the reward is distributed, I\'ll notify you via DMs.',
                             icon_url=interaction.user.avatar.url)
        else:
            embed: discord.Embed = discord.Embed(
                title=':point_up:  You\'re already in!',
                description='You have **already joined** this airdrop.',
                color=discord.Color.red())
            embed.set_footer(text='Just wait patiently for the airdrop to end and the reward to be distributed.',
                             icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def resolve(self, bot: discord.Bot) -> None:
        """
        Resolves the airdrop.
        Note that this doesn't update the DB record - it has to be done through the airdrop manager.
        """

        entrants_to_remove: list[int] = []
        for user_id in self.entrants:
            address: Optional[EthereumAddress] = await DATABASE.get_user_address(user_id)
            if not address:
                entrants_to_remove.append(user_id)
                continue
            logger.log(logging.INFO, f'Sending {self.split}{CONFIG.token_symbol}'
                                     f' to {address} from airdrop {self.message_id}')
            tx_hash: TxHash = await CRYPTO.transfer_erc20(address, self.split)
            embed: discord.Embed = discord.Embed(title=':tada:  Airdrop finished!',
                                                 description=f'You **received your share** of `{self.split}'
                                                             f'{CONFIG.token_symbol}` from an airdrop!\n'
                                                             f'You can view the airdrop summary [here]({self.url})',
                                                 color=0xec850a,
                                                 url=CRYPTO.explorer(tx_hash))
            embed.add_field(name='Transaction Hash', value=f'```c\n{tx_hash}```')
            embed.set_footer(text='Thanks for participating!')
            await (await bot.fetch_user(user_id)).send(embed=embed)
            await asyncio.sleep(0.3)
        message: discord.Message = await (await bot.fetch_channel(self.channel_id)).fetch_message(self.message_id)
        embed: discord.Embed = discord.Embed(title=':tada:  Airdrop finished!',
                                             description=f'The airdrop has **ended** and the reward has been distributed!\n'
                                                         f'```py\nTotal {CONFIG.token_symbol}: {self.amount}\n'
                                                         f'Split ({len(self.entrants)}): {self.split}\n```',
                                             color=CONFIG.token_color,
                                             timestamp=datetime.datetime.fromtimestamp(self.end_time))
        embed.set_footer(text='Ended', icon_url=bot.user.avatar.url)
        await message.edit(embed=embed)

