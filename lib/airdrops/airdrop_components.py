import discord
from .airdrop import Airdrop


class AirdropButton(discord.ui.Button):
    def __init__(self, airdrop: Airdrop):
        """
        A button that can be used to join an airdrop
        """

        self.airdrop: Airdrop = airdrop
        super().__init__(label='Join this airdrop',
                         emoji='\N{money with wings}',
                         style=discord.enums.ButtonStyle.gray,
                         custom_id='airdrop_join')

    async def callback(self, interaction: discord.Interaction):
        """This function will be called any time a user clicks on this button

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object that was created when the user clicked on the button
        """

        try:
            await self.airdrop.join(interaction)
        except discord.NotFound:
            pass
