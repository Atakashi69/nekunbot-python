from bs4 import BeautifulSoup as bs
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import db_articles as db

base_url = 'https://www.hoyolab.com'
genshin_account = '/accountCenter/postList?id=1015537'

async def hoyolab_parse():
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    with Chrome(options=chrome_options) as browser:
        browser.get(base_url + genshin_account)
        html = browser.page_source
    Chrome(options=chrome_options).get(base_url + genshin_account)

    page_soup = bs(html, 'html.parser')
    articles = page_soup.find_all('div', {'class': ['mhy-article-card', 'mhy-account-center-post-card']}, limit=10)
    for article in articles:
        article_id = article.attrs.get('data-log-id-impression')
        print(f'{article_id} is checking')
        #if not (await db.is_article_exists(article_id)):
        # await db.insert_article(article_id)
        #else:
            #continue

        article_url = article.find('a', {'class': 'mhy-article-card__link'}).attrs.get('href')
        article_title = article.find('span', {'class': 'mhy-article-card__text'}).text
        #Grab all links to images in post
        article_image_links = [image.attrs.get('large') for image in article.find_all('div', {'class': 'mhy-article-card__img'})]

        print(article_id, article_url, article_title, article_image_links)

        # TODO: Create function to parse articles insides (videos, text, idk). Parse all <p> tags with 100-250 characters limitation (good idea?)

    #TODO: Create function to create embeds from it^^
