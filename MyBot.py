import discord
from discord.ext import commands, tasks

import Constants
from Utils.HoYoLABParser import HoYoLABParser


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        self.parser = HoYoLABParser(self)

        super().__init__(
            command_prefix=Constants.prefix,
            intents=intents
        )

    async def setup_hook(self):
        print('Hooked')
        self.bg_parse_hoyolab.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    @tasks.loop(minutes=10)
    async def bg_parse_hoyolab(self):
        await self.parser.parse_hoyolab()

    @bg_parse_hoyolab.before_loop
    async def before_parse_hoyolab(self):
        await self.wait_until_ready()