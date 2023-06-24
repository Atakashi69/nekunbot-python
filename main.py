import asyncio
import os

import motor.motor_asyncio
from dotenv import load_dotenv
from webserver import keep_alive

from MyBot import MyBot
from Commands.AdminCommands import AdminCommands
from Commands.HoYoLABCommands import HoYoLABCommands


async def setup() -> None:
    load_dotenv()
    motorClient = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_URI'))
    keep_alive()
    client = MyBot(motorClient)
    await client.add_cog(AdminCommands(client, motorClient))
    await client.add_cog(HoYoLABCommands(client, motorClient))
    await client.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(setup())