import random

import discord
import motor.motor_asyncio
from discord import app_commands
from discord.ext import commands

class SlashCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} cog loaded')

    @app_commands.command(name='command-1', description='command 1 description')
    async def my_slash_command(self, interaction: discord.Interaction, num1:int, num2:int = 4) -> None:
        result = add(num1, num2)
        await interaction.response.send_message(f'Hello from slash command 1! The result is {result}')

    @commands.command(name='command2')
    async def my_command(self, ctx: commands.Context, *args) -> None:
        print(args)
        await ctx.reply(f'Hello from normal command2')

def add(num1, num2):
    return num1 + num2