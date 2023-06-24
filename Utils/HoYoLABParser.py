from discord.ext import commands
from playwright.async_api import async_playwright


class HoYoLABParser:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def parse_hoyolab(self):
        base_url = 'https://www.hoyolab.com'
        genshin_account = '/accountCenter/postList?id=1015537'

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(base_url+genshin_account)

            articles = await page.query_selector_all('div.mhy-article-card')
            articles_to_parse = []

            for article in articles:
                article_id = await article.get_attribute('data-log-id-impression')
                article_url = await (await article.query_selector('a.mhy-article-card__link')).get_attribute('href')
                article_title = await (await article.query_selector('span.mhy-article-card__text')).inner_text()
                article_images = await article.query_selector_all('div.mhy-article-card__img')
                article_images_links = [await image.get_attribute('large') for image in article_images]

                articles_to_parse.append({
                    'article_id': article_id,
                    'article_url': article_url,
                    'article_title': article_title,
                    'article_images_links': article_images_links
                })

            for index, article_to_parse in enumerate(articles_to_parse):
                if index < len(articles_to_parse) - 1 and article_to_parse['article_title'] == articles_to_parse[index + 1]['article_title']:
                    await self.parse_articles_hb(browser, article_to_parse, articles_to_parse[index + 1])
                    continue
                elif index > 0 and article_to_parse['article_title'] == articles_to_parse[index - 1]['article_title']:
                    continue
                else:
                    await self.parse_article(browser, article_to_parse)

            await browser.close()


    #TODO: parse article, extracting title, description, video, something else
    async def parse_article(self, browser, article_to_parse):
        title = article_to_parse['article_title']
        print(title)
        await self.post_article(title)
        pass

    #TODO: merge HB articles here and then post them as one
    async def parse_articles_hb(self, browser, article1, article2):
        print(article1['article_title'])
        pass

    #TODO: change article to needed parameters for an embed
    #TODO: create collection for channel ids to post
    #TODO: create command for adding channel id to database
    async def post_article(self, title):
        pass