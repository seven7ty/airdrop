import discord
from discord.ext import commands
from discord.commands import ApplicationContext, Option
from lib import ETH_ADDRESS_RE
from bot import AirdropBot
from lib.reusable_responses import invalid_address


class UserFacingCommands(commands.Cog):
    def __init__(self, bot: AirdropBot):
        self.bot: AirdropBot = bot

    @commands.slash_command(name='register')
    async def register_command(self,
                               ctx: ApplicationContext,
                               address: Option(str, 'The ETH address you wish to associate with your account')):
        if not (match := ETH_ADDRESS_RE.match(address)):
            await invalid_address(ctx)
            return
        has_prefix: bool = bool(match.groupdict().get('prefix'))
        if not has_prefix:
            address: str = '0x' + address
        await self.bot.db.register_user(ctx.author.id, address)
        embed: discord.Embed = discord.Embed(
            title='Success!',
            color=discord.Color.green(),
            description=f'You have **successfully associated** your account with the address:\n```{address}```'
        )
        embed.set_footer(text='Now just wait for the tips and airdrops to come in!', icon_url=self.bot.user.avatar.url)
        await ctx.respond(embed=embed)


def setup(bot: AirdropBot):
    bot.add_cog(UserFacingCommands(bot))
