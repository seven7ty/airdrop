import discord
from discord.enums import SlashCommandOptionType
from discord.commands import SlashCommandGroup, Option, ApplicationContext

__all__ = ('tip',)

tip: SlashCommandGroup = SlashCommandGroup(name="tip",
                                           description='Commands for sending users, roles and addresses a tip!')


@tip.command(name='user', description='Send a tip to a user.')
@discord.is_owner()
async def tip_user_command(ctx: ApplicationContext,
                           user: Option(discord.Member, description='The user to send the tip to'),
                           amount: Option(SlashCommandOptionType.number, description='The amount of the tip')):
    await ctx.respond(f'Sending {amount} to {user}')


@tip.command(name='role', description='Send a tip to a role.')
@discord.is_owner()
async def tip_role_command(ctx: ApplicationContext,
                           role: Option(discord.Role,
                                        description='The role to send the tip to. '
                                                    'The amount will be split evenly between all members of the role'),
                           amount: Option(SlashCommandOptionType.number, description='The amount of the tip')):
    await ctx.respond(f'Sending {amount} to {role}')


@tip.command(name='address', description='Send a tip to an address.')
@discord.is_owner()
async def tip_address_command(ctx: ApplicationContext,
                              address: Option(SlashCommandOptionType.string,
                                              description='The address to send the tip to'),
                              amount: Option(SlashCommandOptionType.number, description='The amount of the tip')):
    await ctx.respond(f'Sending {amount} to {address}')
