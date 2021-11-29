import discord
from discord.enums import SlashCommandOptionType
from discord.ext import commands
from discord.commands import ApplicationContext, Option
from bot import AirdropBot


class OwnerFacingCommands(commands.Cog):
    def __init__(self, bot: AirdropBot):
        self.bot: AirdropBot = bot


def setup(bot: AirdropBot):
    bot.add_cog(OwnerFacingCommands(bot))
