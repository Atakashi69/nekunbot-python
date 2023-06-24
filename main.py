import asyncio
import os

import motor.motor_asyncio
from dotenv import load_dotenv

from MyBot import MyBot
from Commands.SlashCommands import SlashCommands
from Commands.AdminCommands import AdminCommands
from Commands.HoYoLABCommands import HoYoLABCommands


async def setup() -> None:
    load_dotenv()
    client = MyBot()
    motorClient = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_URI'))
    await client.add_cog(AdminCommands(client))
    await client.add_cog(SlashCommands(client))
    await client.add_cog(HoYoLABCommands(client, motorClient))
    await client.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(setup())