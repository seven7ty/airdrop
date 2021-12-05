import discord


class ConfirmView(discord.ui.View):
    def __init__(self, timeout: int = 30):
        super().__init__(timeout=timeout)
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, _):
        self.value = True
        self.stop()
        button.disabled = True

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, _):
        self.value = False
        self.stop()
        button.disabled = True
