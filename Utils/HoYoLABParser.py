import discord
import motor.motor_asyncio
from discord.ext import commands
from playwright.async_api import async_playwright, Page

import Constants


class HoYoLABParser:
    def __init__(self, bot: commands.Bot, motorClient):
        self.bot = bot
        self.motorClient = motorClient

    async def parse_hoyolab(self):
        base_url = 'https://www.hoyolab.com'
        genshin_account = '/accountCenter/postList?id=1015537'

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(base_url+genshin_account)

            articles = await page.query_selector_all('div.mhy-article-card')
            articles.reverse()
            articles_to_parse = []

            for article in articles:
                article_id = await article.get_attribute('data-log-id-impression')
                if await db_is_article_posted(self.motorClient, article_id):
                    continue
                article_url = await (await article.query_selector('a.mhy-article-card__link')).get_attribute('href')
                article_title = await (await article.query_selector('span.mhy-article-card__text')).inner_text()
                article_info = await (await article.query_selector('p.mhy-article-card__info')).inner_text()
                article_images = await article.query_selector_all('div.mhy-article-card__img')
                article_image_urls = []
                for article_image in article_images:
                    width = await article_image.get_attribute('data-w')
                    height = await article_image.get_attribute('data-h')
                    if (int(height) / int(width)) <= 2:
                        article_image_urls.append(await article_image.get_attribute('large'))

                article_ping = False
                if article_title.startswith('Событие «')\
                        or article_title.startswith('События Молитв')\
                        or article_title.startswith('Специальный стрим')\
                        or article_title.startswith('Функция предзагрузки'):
                    article_ping = True

                articles_to_parse.append({
                    'id': article_id,
                    'url': base_url + article_url,
                    'title': article_title,
                    'info': article_info,
                    'image_urls': article_image_urls,
                    'ping': article_ping
                })

            for index, article_to_parse in enumerate(articles_to_parse):
                if index < len(articles_to_parse) - 1 and article_to_parse['title'] == articles_to_parse[index + 1]['title']:
                    await self.parse_articles_hb(page, article_to_parse, articles_to_parse[index + 1])
                elif index > 0 and article_to_parse['title'] == articles_to_parse[index - 1]['title']:
                    continue
                else:
                    await self.parse_article(page, article_to_parse)

            await browser.close()


    async def parse_article(self, page: Page, article_to_parse):
        description = await get_description(page, article_to_parse['url'])

        await self.post_article(
            article_to_parse['title'],
            description,
            article_to_parse['url'],
            article_to_parse['info'],
            article_to_parse['image_urls'],
            article_to_parse['ping']
        )

        await db_set_article_posted(self.motorClient, article_to_parse['id'])


    async def parse_articles_hb(self, page, article1, article2):
        description = await get_description(page, article1['url'])

        images = []
        for image in article1['image_urls']:
            images.append(image)
        for image in article2['image_urls']:
            images.append(image)

        await self.post_article(
            article1['title'],
            description,
            article1['url'],
            article1['info'],
            images,
            False
        )

        await db_set_article_posted(self.motorClient, article1['id'])
        await db_set_article_posted(self.motorClient, article2['id'])


    async def post_article(self, title, description, url, info, image_urls, ping):
        embeds = []

        embed_main = discord.Embed(title=title, url=url, description=description)
        embed_main.set_footer(text=info)

        if len(image_urls) > 0:
            embed_main.set_image(url=image_urls[0])
        embeds.append(embed_main)
        for index, image_url in enumerate(image_urls):
            if index == 0:
                continue
            embed = discord.Embed(url=url).set_image(url=image_url)
            embeds.append(embed)

        channels = await db_get_channels_genshin_news(self.motorClient)
        for channel in channels:
            content = ''
            if channel['role_id'] and ping:
                content = f'<@&{channel["role_id"]}>'
            await self.bot.get_channel(int(channel['channel_id'])).send(content=content, embeds=embeds)


async def get_description(page: Page, article_url):
    await page.goto(article_url)

    await page.wait_for_selector('div.mhy-article-page__content')

    article_content = await page.query_selector('div.mhy-img-text-article__content')
    if not article_content:
        article_content = await page.query_selector('div.mhy-img-article')
    paragraphs = await article_content.query_selector_all(':scope>p, :scope>h1, :scope>h2, :scope>h3, :scope>h4')
    description = ''
    char_limit = 300
    for paragraph in paragraphs:
        if len(description) < char_limit:
            text = await paragraph.inner_text()
            html = await paragraph.inner_html()

            node_name = str(await paragraph.get_property('nodeName'))
            if node_name.startswith('H'):
                char_limit += len(text)

            links = await paragraph.query_selector_all('a')
            for link in links:
                link_text = await link.inner_text()
                if link_text.strip() == '': continue
                link_url = await link.get_attribute('href')
                char_limit += len(link_url)
                text = text.replace(link_text, f'[{link_text}]({link_url})')

            strongs = await paragraph.query_selector_all('strong')
            for strong in strongs:
                strong_text = await strong.inner_text()
                if strong_text.strip() == '': continue
                text = text.replace(strong_text, f'**{strong_text}**')

            text = text.replace('>>>', '>>').replace('<<<', '<<')
            description += text
            if html != '<br>':
                description += '\n'

    return description.strip()


async def db_is_article_posted(motorClient: motor.motor_asyncio.AsyncIOMotorClient, article_id: str):
    query = {
        'article_id': str(article_id)
    }

    entry = await motorClient[Constants.db_name]['articles_genshin_posted'].find_one(query)
    if entry: return True
    else: return False

async def db_set_article_posted(motorClient: motor.motor_asyncio.AsyncIOMotorClient, article_id: str):
    query = {
        'article_id': str(article_id)
    }
    await motorClient[Constants.db_name]['articles_genshin_posted'].replace_one(filter=query, replacement=query, upsert=True)

async def db_get_channels_genshin_news(motorClient: motor.motor_asyncio.AsyncIOMotorClient):
    channels = []
    async for entry in motorClient[Constants.db_name]['channels_genshin_news'].find({}):
        channels.append(entry)
    return channels