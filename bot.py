import os
import discord
import logging
import importlib
from discord.commands import SlashCommandGroup
from lib import DATABASE, CONFIG, CRYPTO, DatabaseInterface, AirdropManager


class AirdropBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger: logging.Logger = logging.getLogger('discord.Client')
        self._configure_logging()
        self.db: DatabaseInterface = DATABASE
        self.crypto = CRYPTO
        self.airdrop_manager: AirdropManager = AirdropManager(self)
        self._load_cogs()
        self._load_groups()

    def _configure_logging(self):
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s:%(name)s]: %(message)s')
        logging.getLogger('asyncio').setLevel(logging.WARNING)
        logging.getLogger('discord.gateway').setLevel(logging.WARNING)

    def _load_cogs(self):
        for filename in os.listdir(os.path.join(CONFIG.root_directory, 'commands/cogs')):
            if filename.endswith('.py') and not filename.startswith('_'):
                self.load_extension(f'commands.cogs.{filename[:-3]}')
                self.logger.log(logging.INFO, f'Loaded commands.cogs.{filename[:-3]}')

    def _load_groups(self):
        for filename in os.listdir(os.path.join(CONFIG.root_directory, 'commands/groups')):
            if filename.endswith('.py') and not filename.startswith('_'):
                module = importlib.import_module(f'commands.groups.{filename[:-3]}')
                group: SlashCommandGroup = getattr(module, module.__all__[0])  # noqa
                self.add_application_command(group)
                self.logger.log(logging.INFO, f'Loaded commands.groups.{filename[:-3]}')

    async def on_ready(self):
        await self.crypto.setup()
        await self.airdrop_manager.setup()
        self.logger.log(logging.INFO, f'Logged in as {self.user}')


bot = AirdropBot(debug_guild=732952864174899230)
