import asyncio
import math
import random

import discord
import motor.motor_asyncio
from discord import app_commands
from discord.ext import commands
import genshin
from motor.motor_asyncio import AsyncIOMotorClient

from Utils import Constants


class HoYoLABCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, motorClient: motor.motor_asyncio.AsyncIOMotorClient):
        self.bot = bot
        self.motorClient = motorClient
        self.genshinClient = genshin.Client(lang='ru-ru', game=genshin.Game.GENSHIN)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} cog loaded')

    @app_commands.command(name='resin', description='Показывает текущее количество смолы')
    async def resin_slash(self, interaction: discord.Interaction, mention: discord.Member = None, uid: int = None):
        await interaction.response.defer()
        discordID, uid, error_msg = param_check(mention, uid, interaction.user.id)
        if error_msg:
            await interaction.followup.send(error_msg)
            return
        uid, cookie, error_msg = await db_get_cookies(self.motorClient, discordID, uid)
        if error_msg:
            await interaction.followup.send(error_msg)
            return
        notes, error_msg = await get_notes(self.genshinClient, uid, cookie)
        if error_msg:
            await interaction.followup.send(error_msg)
            return

        msg = get_resin_msg(uid, notes)

        await interaction.followup.send(msg)

    @commands.command(name='resin')
    async def resin_normal(self, ctx: commands.Context, *args):
        discordID, uid, error_msg = args_check(args, ctx.author.id)
        if error_msg:
            await ctx.reply(error_msg)
            return
        uid, cookie, error_msg = await db_get_cookies(self.motorClient, discordID, uid)
        if error_msg:
            await ctx.reply(error_msg)
            return
        notes, error_msg = await get_notes(self.genshinClient, uid, cookie)
        if error_msg:
            await ctx.reply(error_msg)
            return

        msg = get_resin_msg(uid, notes)

        await ctx.reply(msg)

    @app_commands.command(name='notes', description='Показывает ваши игровые заметки')
    async def notes_slash(self, interaction: discord.Interaction, mention: discord.Member = None, uid: int = None):
        await interaction.response.defer()
        discordID, uid, error_msg = param_check(mention, uid, interaction.user.id)
        if error_msg:
            await interaction.followup.send(error_msg)
            return
        uid, cookie, error_msg = await db_get_cookies(self.motorClient, discordID, uid)
        if error_msg:
            await interaction.followup.send(error_msg)
            return
        notes, error_msg = await get_notes(self.genshinClient, uid, cookie)
        if error_msg:
            await interaction.followup.send(error_msg)
            return

        msg = get_notes_msg(uid, notes)

        await interaction.followup.send(msg)

    @commands.command(name='notes')
    async def notes_normal(self, ctx: commands.Context, *args):
        discordID, uid, error_msg = args_check(args, ctx.author.id)
        if error_msg:
            await ctx.reply(error_msg)
            return
        uid, cookie, error_msg = await db_get_cookies(self.motorClient, discordID, uid)
        if error_msg:
            await ctx.reply(error_msg)
            return
        notes, error_msg = await get_notes(self.genshinClient, uid, cookie)
        if error_msg:
            await ctx.reply(error_msg)
            return

        msg = get_notes_msg(uid, notes)

        await ctx.reply(msg)

    @app_commands.command(name='auth', description='Авторизует вас в системе')
    async def auth_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.user.send(Constants.util_messages.auth1)
        await interaction.user.send(Constants.util_messages.auth2)

        await interaction.followup.send(':envelope: Проверьте личные сообщения!')

        def cookie_check(m: discord.Message):
            return m.author.id == interaction.user.id and m.guild is None and m.content.__contains__('ltoken') and m.content.__contains__('ltuid')
        def uid_check(m: discord.Message):
            return m.author.id == interaction.user.id and m.guild is None and len(m.content) == 9

        try:
            cookie = await interaction.client.wait_for('message', check=cookie_check, timeout=60*30)
            await interaction.user.send('Отлично, теперь отправьте мне ваш UID')
            uid = await interaction.client.wait_for('message', check=uid_check, timeout=60*10)
            await db_set_cookies(self.motorClient, interaction.user.id, int(uid.content), cookie.content)
            await interaction.user.send(':white_check_mark: UID был обновлён в базе данных')
        except asyncio.TimeoutError:
            await interaction.user.send(Constants.error_messages.timed_out)

    @commands.command(name='auth')
    async def auth_normal(self, ctx: commands.Context):
        await ctx.author.send(Constants.util_messages.auth1)
        await ctx.author.send(Constants.util_messages.auth2)

        await ctx.reply(':envelope: Провеьте личные сообщения!')

        def cookie_check(m: discord.Message):
            return m.author.id == ctx.author.id and m.guild is None and m.content.__contains__('ltoken') and m.content.__contains__('ltuid')
        def uid_check(m: discord.Message):
            return m.author.id == ctx.author.id and m.guild is None and len(m.content) == 9

        try:
            cookie = await ctx.bot.wait_for('message', check=cookie_check, timeout=60*30)
            await ctx.author.send('Отлично, теперь отправьте мне ваш UID')
            uid = await ctx.bot.wait_for('message', check=uid_check, timeout=60 * 10)
            await db_set_cookies(self.motorClient, ctx.author.id, int(uid.content), cookie.content)
            await ctx.author.send(':white_check_mark: UID был обновлён в базе данных')
        except asyncio.TimeoutError:
            await ctx.author.send(Constants.error_messages.timed_out)

def param_check(mention: discord.Member, uid: int, authorID: int):
    if mention and uid:
        return None, None, Constants.error_messages.too_much_arguments
    if mention:
        discordID = mention.id
        uid = None
    elif uid:
        discordID = None
        if len(str(uid)) != 9:
            return None, None, Constants.error_messages.wrong_uid
    else:
        discordID = authorID
        uid = None

    return discordID, uid, None


def args_check(args, authorID: int):
    if len(args) > 1:
        return None, None, Constants.error_messages.too_much_arguments
    if len(args) > 0:
        if args[0].startswith('<@') and args[0].endswith('>'):
            discordID = args[0][2:-1]
            uid = None
        else:
            discordID = None
            if len(str(args[0])) != 9:
                return None, None, Constants.error_messages.wrong_uid
            uid = int(args[0])
    else:
        discordID = authorID
        uid = None

    return discordID, uid, None


def get_resin_msg(uid, notes):
    resin_full = (notes.current_resin == notes.max_resin)

    msg = f'[{uid}]\n' \
          f':crescent_moon: Смола: {notes.current_resin}/{notes.max_resin}' \
          f'{" :bangbang:" if resin_full else (chr(10)+":clock3: До полного восстановленния: "+str(notes.remaining_resin_recovery_time))}'

    return msg


def get_notes_msg(uid, notes):
    resin_full = (notes.current_resin == notes.max_resin)

    realm_currency_recovery_time_ru = translate_timedelta(notes.remaining_realm_currency_recovery_time)
    realm_full = realm_currency_recovery_time_ru == ''

    transformer_recovery_time_ru = translate_transformer_timedelta(notes.remaining_transformer_recovery_time)
    transformer = transformer_recovery_time_ru != ''

    expeditions_list = get_expeditions_list(notes.expeditions)

    msg = f'[{uid}]\n' \
          f':notebook_with_decorative_cover: **Игровые заметки**\n' \
          f':crescent_moon: Смола: {notes.current_resin}/{notes.max_resin}' \
          f'{" :bangbang:" if resin_full else (chr(10)+":clock3: До полного восстановленния: "+str(notes.remaining_resin_recovery_time))}\n' \
          f':date: Выполнено поручений: {notes.completed_commissions}/{notes.max_commissions}, ' \
          f'доп. награда {"собрана :white_check_mark:" if notes.claimed_commission_reward else "не собрана :x:"}\n' \
          f':money_with_wings: Скидки на боссов: {notes.remaining_resin_discounts}\n' \
          f':moneybag: Сокровища обители: {notes.current_realm_currency}/{notes.max_realm_currency}' \
          f'{" :bangbang:" if realm_full else (chr(10)+":clock3: До полного восстановленния: "+realm_currency_recovery_time_ru)}\n' \
          f':recycle: Преобразователь: {"собран" if transformer else "не собран"}' \
          f'{" :x:" if not transformer else (", будет готов через " + transformer_recovery_time_ru)+" :white_check_mark:"}\n' \
          f':mag: Начато экспедиций: {len(notes.expeditions)}/{notes.max_expeditions}\n' \
          f'{expeditions_list}'

    return msg


def get_expeditions_list(expeditions):
    results = []
    for expedition in expeditions:
        print(expedition)
        if expedition.finished:
            result = f'\t:pushpin: Завершена'
        else:
            emoji = f':clock{random.randint(1, 12)}:'
            result = f'\t{emoji} Осталось времени: {expedition.remaining_time}'
        results.append(result)
    return '\n'.join(results)


def translate_timedelta(timedelta):
    result = ''
    if not timedelta: return result
    total_seconds = timedelta.total_seconds()
    days = timedelta.days
    hours = math.floor((total_seconds - days * (60*60*24)) / 3600)
    minutes = math.floor((total_seconds - days * (60*60*24) - hours * (60*60)) / 60)
    seconds = math.floor(total_seconds - days * (60*60*24) - hours * (60*60) - minutes * 60)

    if days > 0: result += str(days) + 'д. '
    if hours > 0: result += str(hours) + 'ч. '
    if minutes > 0: result += str(minutes) + 'м. '
    if seconds > 0: result += str(seconds) + 'с.'
    return result.strip()


def translate_transformer_timedelta(transformer_timedelta):
    result = ''
    if not transformer_timedelta: return result
    if transformer_timedelta.days == 0:
        if transformer_timedelta.hours > 0: result += str(transformer_timedelta.hours) + 'ч. '
        if transformer_timedelta.minutes > 0: result += str(transformer_timedelta.hours) + ' м. '
        if transformer_timedelta.seconds > 0: result += str(transformer_timedelta.seconds) + ' с.'
    else:
        if transformer_timedelta.days < 2: result = str(transformer_timedelta.days) + ' день'
        elif transformer_timedelta.days < 5: result = str(transformer_timedelta.days) + ' дня'
        else: result = str(transformer_timedelta.days) + ' дней'
    return result.strip()


async def get_notes(genshinClient: genshin.Client, uid: int, cookie: str):
    ltuid = (cookie.partition('ltuid=')[-1]).partition(';')[0]
    ltoken = (cookie.partition('ltoken=')[-1]).partition(';')[0]

    genshinClient.set_cookies({'ltuid': ltuid, 'ltoken': ltoken})
    try:
        notes = await genshinClient.get_genshin_notes(uid)
        return notes, None
    except genshin.CookieException as e:
        print(e)
        return None, Constants.error_messages.invalid_cookie


async def db_set_cookies(motorClient: AsyncIOMotorClient, discordID: int, UID: int, cookie: str):
    query_filter = {
       'discordID': str(discordID)
    }
    query = {
        'discordID': str(discordID),
        'UID': UID,
        'cookie': cookie
    }
    await motorClient[Constants.db_name]['hoyolab_cookies'].replace_one(filter=query_filter, replacement=query, upsert=True)


async def db_get_cookies(motorClient: AsyncIOMotorClient, discordID: int, UID: int):
    if discordID:
        query = {'discordID': str(discordID)}
    elif UID:
        query = {'UID': UID}
    else:
        return None, None

    entry = await motorClient[Constants.db_name]['hoyolab_cookies'].find_one(query)
    if not entry:
        return None, None, Constants.error_messages.auth_fail
    return entry['UID'], entry['cookie'], None
