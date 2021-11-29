from discord.ext import commands
from bot import AirdropBot


class EventHandler(commands.Cog):
    def __init__(self, bot: AirdropBot):
        self.bot: AirdropBot = bot


def setup(bot: AirdropBot):
    bot.add_cog(EventHandler(bot))
