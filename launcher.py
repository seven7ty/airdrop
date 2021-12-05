import os
from bot import bot
from lib import CONFIG


if __name__ == '__main__':
    if os.name != 'nt':
        __import__('uvloop').install()
    bot.run(CONFIG.env('DISCORD_BOT_TOKEN'))
