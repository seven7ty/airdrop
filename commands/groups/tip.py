import discord
from discord.enums import SlashCommandOptionType
from discord.commands import SlashCommandGroup, Option, ApplicationContext
from lib.types import EthereumAddress, TxHash
from lib import CONFIG, tip_notification
from typing import Optional

__all__ = ('tip',)

tip: SlashCommandGroup = SlashCommandGroup(name="tip",
                                           description='Commands for sending users, roles and addresses a tip!')


@tip.command(name='user', description='Send a tip to a user')
@discord.is_owner()
async def tip_user_command(ctx: ApplicationContext,
                           user: Option(discord.Member, description='The user to send the tip to'),
                           amount: Option(SlashCommandOptionType.number, description='The amount of the tip')):
    associated_address: Optional[EthereumAddress] = await ctx.bot.db.get_user_address(user.id)
    if not associated_address:
        embed = discord.Embed(title='Oh no!',
                              description=f'{user.mention} **hasn\'t set their address yet!**',
                              color=discord.Color.red())
        embed.set_footer(text='Tell them to use the register command!', icon_url=ctx.bot.user.avatar.url)
        await ctx.respond(embed=embed)
        return
    tx_hash: TxHash = await ctx.bot.crypto.transfer_erc20(associated_address, amount)
    embed = discord.Embed(title=':rocket:  Tip sent!',
                          description=f'{user.mention} **has been tipped** `{amount}{CONFIG.token_symbol}`!',
                          color=discord.Color.green(),
                          url=ctx.bot.crypto.explorer(tx_hash))
    embed.add_field(name='Transaction Hash', value=f'```c\n{tx_hash}```')
    embed.set_footer(text='I notified them via DMs, see ya!', icon_url=ctx.bot.user.avatar.url)
    await tip_notification(ctx, user, amount, tx_hash)
    await ctx.respond(embed=embed)


@tip.command(name='role', description='Send a tip to a role')
@discord.is_owner()
async def tip_role_command(ctx: ApplicationContext,
                           role: Option(discord.Role,
                                        description='The role to send the tip to. '
                                                    'The amount will be split evenly between all members of the role'),
                           amount: Option(SlashCommandOptionType.number, description='The amount of the tip')):
    await ctx.respond(f'Sending {amount} to {role}')


@tip.command(name='address', description='Send a tip to an address')
@discord.is_owner()
async def tip_address_command(ctx: ApplicationContext,
                              address: Option(SlashCommandOptionType.string,
                                              description='The address to send the tip to'),
                              amount: Option(SlashCommandOptionType.number, description='The amount of the tip')):
    await ctx.respond(f'Sending {amount} to {address}')
