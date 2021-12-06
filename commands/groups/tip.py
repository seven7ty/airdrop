import discord
from discord.enums import SlashCommandOptionType
from discord.commands import SlashCommandGroup, Option, ApplicationContext
from lib.types import EthereumAddress, TxHash
from lib import (CONFIG, tip_notification, CRYPTO, ConfirmView,
                 shorten_address, ETH_ADDRESS_RE, invalid_address, insufficient_funds, BalanceTooLow)
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
    try:
        tx_hash: TxHash = await CRYPTO.transfer_erc20(associated_address, CRYPTO.to_contract_value(amount))
    except BalanceTooLow:
        await insufficient_funds(ctx, amount)
        return
    embed = discord.Embed(title=':rocket:  Tip sent!',
                          description=f'{user.mention} **has been tipped** `{amount}{CONFIG.token_symbol}`!',
                          color=discord.Color.green(),
                          url=CRYPTO.explorer(tx_hash))
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
    if not await CRYPTO.can_afford(CRYPTO.to_contract_value(amount)):
        await insufficient_funds(ctx, amount)
        return
    addresses: dict[discord.Member, EthereumAddress] = await ctx.bot.db.get_role_addresses(role)
    split: float = amount / len(addresses)
    if not role.members:
        embed = discord.Embed(title='Nah uh!',
                              description=f'{role.mention} **has no members!**',
                              color=discord.Color.red())
        embed.set_footer(text='Give the role to some people first!', icon_url=ctx.bot.user.avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)
        return
    if not addresses:
        embed = discord.Embed(title='Oh no!',
                              description=f'None of the users in {role.mention} have an address set!!',
                              color=discord.Color.red())
        embed.set_footer(text='Tell them to use the register command!', icon_url=ctx.bot.user.avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)
        return
    if len(addresses) != len(role.members):
        embed = discord.Embed(title='Here\'s the thing...',
                              description=f'Out of {len(role.members)} members of {role.mention}, **only {len(addresses)} have set their addresses!**',
                              color=discord.Color.blurple())
        embed.set_footer(text=f'Do you wish to carry out the tip anyway?\nEach of the members will receive {split}{CONFIG.token_symbol}', icon_url=ctx.bot.user.avatar.url)
        confirmation: ConfirmView = ConfirmView(f'Tip anyway ({len(addresses)})', 'Cancel')
        await ctx.respond(embed=embed, view=confirmation)
        await confirmation.wait()
        if not confirmation.value:
            embed_cancelled: discord.Embed = discord.Embed(title=':small_red_triangle_down:  Not this time then!',
                                                           description=f'**No transactions** were made!',
                                                           color=0xE2586D)
            await ctx.respond(embed=embed_cancelled, ephemeral=True)
            return
    tx_hashes: list[TxHash] = await CRYPTO.group_payout(addresses.values(), CRYPTO.to_contract_value(split))
    embed: discord.Embed = discord.Embed(title=':rocket:  Tip sent!',
                                         description=f'{len(addresses)} members of {role.mention} **have been tipped** `{split}{CONFIG.token_symbol} each`!',
                                         color=discord.Color.green())
    embed.set_footer(text='I notified them via DMs, see ya!', icon_url=ctx.bot.user.avatar.url)
    await ctx.respond(embed=embed)
    for (member, address), tx in zip(addresses.items(), tx_hashes):
        await tip_notification(ctx, member, split, tx)


@tip.command(name='address', description='Send a tip to an address')
@discord.is_owner()
async def tip_address_command(ctx: ApplicationContext,
                              address: Option(SlashCommandOptionType.string,
                                              description='The address to send the tip to'),
                              amount: Option(SlashCommandOptionType.number, description='The amount of the tip')):
    if not ETH_ADDRESS_RE.match(address):
        await invalid_address(ctx)
        return
    try:
        tx_hash: TxHash = await CRYPTO.transfer_erc20(address, CRYPTO.to_contract_value(amount))
    except BalanceTooLow:
        await insufficient_funds(ctx, amount)
        return
    embed = discord.Embed(title=':rocket:  Tip sent!',
                          description=f'`{amount}{CONFIG.token_symbol}` **has been sent** to `{shorten_address(address)}`!',
                          color=discord.Color.green(),
                          url=CRYPTO.explorer(tx_hash))
    embed.add_field(name='Transaction Hash', value=f'```c\n{tx_hash}```')
    await ctx.respond(embed=embed)
