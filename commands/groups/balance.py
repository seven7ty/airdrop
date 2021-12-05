import discord
from discord.commands import SlashCommandGroup, Option, ApplicationContext
from lib.types import EthereumAddress
from lib import (CONFIG, ETH_ADDRESS_RE,
                 no_associated_address_user, invalid_address,
                 shorten_address, no_associated_address_you)


__all__ = ('balance',)

balance: SlashCommandGroup = SlashCommandGroup(name="balance",
                                               description='Commands for getting the balance of a user or address')


@balance.command(name='address',
                 description=f'Get the {CONFIG.token_symbol} balance of an address')
async def balance_command(ctx: ApplicationContext,
                          address: Option(str, f'The ETH address whose {CONFIG.token_symbol} '
                                               f'balance you want to check')):
    if not (match := ETH_ADDRESS_RE.match(address)):
        await invalid_address(ctx)
        return
    if not bool(match.groupdict().get('prefix')):
        address: str = '0x' + address
    embed: discord.Embed = discord.Embed(title=f':money_with_wings:  {CONFIG.token_symbol} balance'
                                               f' of `{shorten_address(address)}`',
                                         url=ctx.bot.crypto.explorer(address, 'address'),
                                         color=0xec850a,
                                         description=f'```c\n{await ctx.bot.crypto.get_erc20_balance(address)}'
                                                     f' {CONFIG.token_symbol}```')
    embed.set_footer(text='You can tap the title to view the address on blockchain explorer!',
                     icon_url=ctx.bot.user.avatar.url)
    await ctx.respond(embed=embed)


@balance.command(name='user',
                 description=f'Get {CONFIG.token_symbol} the balance of a user')
async def balance_command(ctx: ApplicationContext,
                          user: Option(discord.Member, f'The user whose {CONFIG.token_symbol} '
                                                       f'balance you want to check', required=False)):
    is_author: bool = user is None
    if not user:
        user = ctx.author
    user_str: str = user.name + "'s" if not user.id == ctx.author.id else 'Your'
    address: EthereumAddress = await ctx.bot.db.get_user_address(user.id)
    if not address:
        if is_author:
            await no_associated_address_you(ctx)
        else:
            await no_associated_address_user(ctx, user)
        return
    embed: discord.Embed = discord.Embed(title=f':money_with_wings:  {user_str} {CONFIG.token_symbol} balance',
                                         url=ctx.bot.crypto.explorer(address, 'address'),
                                         color=0xec850a,
                                         description=f'```c\n{await ctx.bot.crypto.get_erc20_balance(address)}'
                                                     f' {CONFIG.token_symbol}```')
    embed.set_footer(text='You can tap the title to view the address on blockchain explorer!',
                     icon_url=ctx.bot.user.avatar.url)
    await ctx.respond(embed=embed)
