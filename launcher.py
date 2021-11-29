from bot import bot
from lib import CONFIG


if __name__ == '__main__':
    bot.run(CONFIG.env('DISCORD_BOT_TOKEN'))
