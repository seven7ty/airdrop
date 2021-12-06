import discord
from discord.commands import ApplicationContext
from typing import Union, TYPE_CHECKING
if TYPE_CHECKING:
    from .types import TxHash
from . import CONFIG

__all__: tuple = ('invalid_address', 'no_associated_address_you',
                  'tip_notification', 'no_associated_address_user',
                  'invalid_duration', 'insufficient_funds')


async def invalid_address(ctx: ApplicationContext):
    embed: discord.Embed = discord.Embed(
        title='Uh oh!',
        color=discord.Color.red(),
        description=f'**That\'s not a valid ETH address!** Please try again.'
    )
    embed.set_footer(text='Tip: an ETH address starts with 0x and is 40 characters long',
                     icon_url=ctx.bot.user.avatar.url)
    await ctx.respond(embed=embed)


async def no_associated_address_you(ctx: ApplicationContext, footer: str = ''):
    embed: discord.Embed = discord.Embed(
        title='Uh oh!',
        color=discord.Color.red(),
        description=f'**You have not associated an address with your account!**\n'
                    f'Please use the `register` command to do so.'
    )
    if footer:
        embed.set_footer(text=footer, icon_url=ctx.bot.user.avatar.url)
    await ctx.respond(embed=embed)


async def no_associated_address_user(ctx: ApplicationContext, user: discord.Member, footer: str = ''):
    embed: discord.Embed = discord.Embed(
        title='Uh oh!',
        color=discord.Color.red(),
        description=f'{user.mention} **has not associated an address with their account!**\n'
                    f'They can use the `register` command to do so.'
    )
    if footer:
        embed.set_footer(text=footer, icon_url=ctx.bot.user.avatar.url)
    await ctx.respond(embed=embed)


async def tip_notification(ctx: ApplicationContext, user: discord.Member, amount: Union[int, float], tx_hash: 'TxHash'):
    embed: discord.Embed = discord.Embed(title=':tada:  You received a tip!',
                                         description=f'You **have been tipped** `{amount}{CONFIG.token_symbol}`'                                                     f' by {ctx.author.mention}!',
                                         color=0xec850a,
                                         url=ctx.bot.crypto.explorer(tx_hash))  # noqa
    embed.add_field(name='Transaction Hash', value=f'```c\n{tx_hash}```')
    embed.set_footer(text='Enjoy your gift, see ya around!', icon_url=ctx.bot.user.avatar.url)
    await user.send(embed=embed)


async def invalid_duration(ctx: ApplicationContext):
    embed: discord.Embed = discord.Embed(title='Uh oh!',
                                         description=f'That\'s **not a valid duration.**\n'
                                                     f'You can see supported formats [here](https://bit.ly/3IdJBSP)',
                                         color=discord.Color.red())
    await ctx.respond(embed=embed, ephemeral=True)


async def insufficient_funds(ctx: ApplicationContext, amount: Union[int, float]):
    embed: discord.Embed = discord.Embed(title='Uh oh!',
                                         description=f'You **don\'t have enough funds** to send a TX with `{amount}{CONFIG.token_symbol}`!',
                                         color=discord.Color.red())
    await ctx.respond(embed=embed, ephemeral=True)
