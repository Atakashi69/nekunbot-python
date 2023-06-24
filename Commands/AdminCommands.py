import os

import discord
from discord import app_commands
from discord.ext import commands


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} cog loaded')

    @commands.command()
    async def sync(self, ctx:commands.Context) -> None:
        if str(ctx.author.id) != os.getenv('OWNER_ID'):
            await ctx.reply('You are not my master!')
            return
        cmds = await ctx.bot.tree.sync()
        await ctx.reply(f'Synced {len(cmds)} commands')