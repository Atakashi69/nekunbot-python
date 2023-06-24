import os

from discord.ext import commands

from Utils import Constants


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, motorClient):
        self.bot = bot
        self.motorClient = motorClient

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} cog loaded')

    @commands.command()
    async def sync(self, ctx: commands.Context):
        if str(ctx.author.id) != os.getenv('OWNER_ID'):
            await ctx.reply(Constants.error_messages.not_my_master)
            return
        cmds = await ctx.bot.tree.sync()
        await ctx.reply(f'Synced {len(cmds)} commands')

    @commands.command()
    async def gnews(self, ctx: commands.Context, *args):
        if len(args) == 0 or len(args) > 2:
            await ctx.reply(Constants.error_messages.wrong_amount_arguments)
            return
        channel_id = args[0]
        if not channel_id.startswith('<#') and not channel_id.endswith('>'):
            await ctx.reply(Constants.error_messages.wrong_arguments)
            return
        role_id = ''
        if len(args) == 2:
            role_id = args[1]
        if role_id and not role_id.startswith('<@&') and not role_id.endswith('>'):
            await ctx.reply(Constants.error_messages.wrong_arguments)
            return
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply(Constants.error_messages.not_admin)
            return

        await db_set_channels_genshin_news(self.motorClient, ctx.guild.id, channel_id[2:-1], role_id[3:-1])
        await ctx.reply(Constants.util_messages.channel_connected)


async def db_set_channels_genshin_news(motorClient, guild_id: int, channel_id: int, role_id: int):
    query_filter = {
        'guild_id': str(guild_id)
    }
    query = {
        'guild_id': str(guild_id),
        'channel_id': str(channel_id),
        'role_id': str(role_id)
    }

    await motorClient[Constants.db_name]['channels_genshin_news'].replace_one(filter=query_filter, replacement=query, upsert=True)