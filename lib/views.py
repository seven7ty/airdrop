import discord


class ConfirmViewButton(discord.ui.Button):
    def __init__(self, role: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role: bool = role

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.role
        self.view.stop()


class ConfirmView(discord.ui.View):
    def __init__(self, yes_label: str = 'Confirm', no_label: str = 'Cancel', timeout: int = 60):
        super().__init__(timeout=timeout)
        self.value = None
        self.add_item(ConfirmViewButton(True, label=yes_label, style=discord.ButtonStyle.green))
        self.add_item(ConfirmViewButton(False, label=no_label))

