import discord
from discord.enums import SlashCommandOptionType
from discord.ext import commands, tasks
from discord.commands import ApplicationContext, Option
from pytimeparse.timeparse import timeparse
from lib import CONFIG, invalid_duration, ConfirmView, Airdrop, AirdropNotFound
from bot import AirdropBot
from typing import Union, Optional


class OwnerFacingCommands(commands.Cog):
    def __init__(self, bot: AirdropBot):
        self.bot: AirdropBot = bot
        self.airdrop_worker_loop.start()

    @tasks.loop(seconds=10)
    async def airdrop_worker_loop(self):
        await self.bot.airdrop_manager.frame()

    @airdrop_worker_loop.before_loop
    async def __wait(self):
        await self.bot.wait_until_ready()

    @discord.command(name='airdrop',
                     description=f'Create an {CONFIG.token_symbol} airdrop, in the current or specified channel.')
    @discord.is_owner()
    @commands.guild_only()
    async def airdrop_command(self,
                              ctx: ApplicationContext,
                              amount: Option(SlashCommandOptionType.number,
                                             description=f'The amount of {CONFIG.token_symbol} to use for this airdrop'),
                              duration: Option(SlashCommandOptionType.string,
                                               description='The duration of the airdrop'),
                              channel: Option(discord.TextChannel,
                                              description='The channel to send the airdrop in, or the current one if'
                                                          ' not specified.',
                                              required=False)):
        if channel is None:
            channel = ctx.channel
        if not isinstance(channel, discord.TextChannel):
            await ctx.respond(f'{channel} is not a text channel.', ephemeral=True)
            return
        time: Union[int, float] = timeparse(duration)
        if not time:
            await invalid_duration(ctx)
            return
        if time < 15:
            err_embed: discord.Embed = discord.Embed(title='Nope!',
                                                     description=f'Airdrop duration must be **at least 15 seconds**.',
                                                     color=discord.Color.red())
            await ctx.respond(embed=err_embed, ephemeral=True)
            return
        elif time > 60 * 60 * 24 * 7:
            err_embed: discord.Embed = discord.Embed(title='Nope!',
                                                     description=f'Airdrops can\'t last **longer than a week!**',
                                                     color=discord.Color.red())
            await ctx.respond(embed=err_embed, ephemeral=True)
            return
        confirmation = ConfirmView()
        confirmation_embed: discord.Embed = discord.Embed(title='Airdrop Confirmation',
                                                          description=f'The airdrop will be sent to {channel.mention}'
                                                                      f' **with** `{amount}{CONFIG.token_symbol}`'
                                                                      f' **bound.**\nYou can cancel this airdrop before'
                                                                      f' its due time by right clicking the airdrop'
                                                                      f' message and selecting `Cancel Airdrop`.',
                                                          color=discord.Color.blurple())
        confirmation_embed.set_footer(text=f'Select Confirm to proceed.', icon_url=self.bot.user.avatar.url)
        await ctx.respond(embed=confirmation_embed, view=confirmation, ephemeral=True)
        await confirmation.wait()
        if not confirmation.value:
            embed_cancelled: discord.Embed = discord.Embed(title=':small_red_triangle_down:  Maybe next time...',
                                                           description=f'The airdrop was **cancelled.**',
                                                           color=0xE2586D)
            await ctx.respond(embed=embed_cancelled, ephemeral=True)
        else:
            embed_confirmed: discord.Embed = discord.Embed(title=':white_check_mark:  Airdrop confirmed!',
                                                           description='The airdrop will finish in Remember,'
                                                                       ' you can cancel the airdrop by'
                                                                       ' right-clicking it and selecting'
                                                                       ' `Cancel Airdrop`.',
                                                           color=0x77B255)
            await ctx.respond(embed=embed_confirmed, ephemeral=True)
            await self.bot.airdrop_manager.new_airdrop(ctx, amount, time, channel=channel)

    @discord.message_command(name='Cancel Airdrop')
    @commands.guild_only()
    async def cancel_airdrop_context_menu(self, ctx: ApplicationContext, message: discord.Message):
        if ctx.user.id not in CONFIG.admins:
            return await ctx.respond(f'You **do not have permission** to cancel an airdrop!', ephemeral=True)
        try:
            airdrop: Optional[Airdrop] = self.bot.airdrop_manager.get_airdrop(message.id)
        except AirdropNotFound:
            embed: discord.Embed = discord.Embed(title='Nope!',
                                                 description=f'This message is not an airdrop.',
                                                 color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            confirmation = ConfirmView()
            confirmation_embed: discord.Embed = discord.Embed(title='Airdrop Confirmation',
                                                              description=f'Are you sure you want to cancel this airdrop?',
                                                              color=discord.Color.blurple())
            confirmation_embed.set_footer(text=f'Select Confirm to proceed.', icon_url=self.bot.user.avatar.url)
            await ctx.respond(embed=confirmation_embed, view=confirmation, ephemeral=True)
            await confirmation.wait()
            if not confirmation.value:
                embed_cancelled: discord.Embed = discord.Embed(title=':small_red_triangle_down:  Not this time then!',
                                                               description=f'The airdrop was **not cancelled.**',
                                                               color=0xE2586D)
                await ctx.respond(embed=embed_cancelled, ephemeral=True)
            else:
                embed_confirmed: discord.Embed = discord.Embed(title=':outbox_tray:  Airdrop cancelled!',
                                                               description=f'The airdrop was **cancelled.**',
                                                               color=CONFIG.token_color)
                embed_confirmed.set_footer(text=f'I notified the entrants about the cancellation via DMs',
                                           icon_url=self.bot.user.avatar.url)
                await ctx.respond(embed=embed_confirmed, ephemeral=True)
                await self.bot.airdrop_manager.cancel(airdrop)


def setup(bot: AirdropBot):
    bot.add_cog(OwnerFacingCommands(bot))
