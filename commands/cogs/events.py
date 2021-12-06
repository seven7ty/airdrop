import logging
import discord
from discord.ext import commands
from bot import AirdropBot
from lib import AirDropInteractionType, Airdrop


class EventHandler(commands.Cog):
    def __init__(self, bot: AirdropBot):
        self.bot: AirdropBot = bot

    # yes, I do realize that persistent views are a thing, but this works just as well
    # and I also found it to be more reliable
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        try:
            if interaction.is_component() and (custom_id := interaction.data.get('custom_id')):
                if custom_id in [ait.value for ait in AirDropInteractionType]:
                    if (type_ := AirDropInteractionType(custom_id)) is AirDropInteractionType.JOIN:
                        airdrop: Airdrop = self.bot.airdrop_manager.get_airdrop(interaction.message.id)
                        await airdrop.join(interaction)
                    else:
                        self.bot.logger.log(logging.WARNING, f'Unknown long-lasting interaction type: {type_}')
        except discord.NotFound:
            pass


def setup(bot: AirdropBot):
    bot.add_cog(EventHandler(bot))
