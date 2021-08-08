from datetime import datetime

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from celery.utils.log import get_task_logger

from financial_news.models import FinancialSymbol, FinancialNews

logger_cl = get_task_logger(__name__)


@shared_task
def scraping_task():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        symbols_for_scraping = get_scraping_symbols()
        for symbol in symbols_for_scraping:
            url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US" % (symbol,)
            scraped_news = fetch_financial_news_by_url(url, headers)
            save_to_db_scraped_financial_news_for_symbol(symbol, scraped_news)

    except Exception as e:
        logger_cl.exception(e)


def get_scraping_symbols():
    """ Function that returns financial symbols for scraping
    :return financial symbols
    :rtype: list
    """

    try:
        scraping_symbols = FinancialSymbol.objects.filter(scraping_on=True)
        return [scrap_symbol.symbol for scrap_symbol in scraping_symbols]
    except Exception as e:
        logger_cl.exception(e)
        return []


def fetch_financial_news_by_url(url, headers):
    """ Function that returns scraped news for url
    :param url: scraping url
    :type url: str
    :param headers: url header
    :type headers: dict
    :return scraped news or False
    :rtype: list or boolean
    """

    financial_news = []
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'xml')
        s_items = soup.find_all('item')
        for item in s_items:
            item_guid = item.find('guid')
            item_title = item.find('title')
            item_description = item.find('description')
            item_link = item.find('link')
            item_pubDate = item.find('pubDate')

            financial_news.append({
                'guid': item_guid.text if item_guid is not None else False,
                'title': item_title.text if item_title is not None else False,
                'description': item_description.text if item_description is not None else False,
                'link': item_link.text if item_link is not None else False,
                'pubDate': item_pubDate.text if item_pubDate is not None else False,
            })
        return financial_news
    else:
        logger_cl.error('Error in getting finance data for url: %s and header: %s' % (url, headers))
        return False


def save_to_db_scraped_financial_news_for_symbol(f_symbol, scraped_news):
    """ Function that save scraped news to db
    :param f_symbol: scraped financial symbol
    :type f_symbol: str
    :param scraped_news: scraped news
    :type scraped_news: list
    :return None
    """

    pub_date_format = '%a, %d %b %Y %H:%M:%S %z'
    f_symbol_inst = FinancialSymbol.objects.get(symbol=f_symbol)

    for scraped_item in scraped_news:
        logger_cl.debug('Saving news item: %s' % (scraped_item,))
        item_guid = scraped_item['guid']
        item_title = scraped_item['title']
        item_description = scraped_item['description']
        item_link = scraped_item['link']
        item_pubDate = scraped_item['pubDate']

        if item_guid is not False:
            if not FinancialNews.objects.filter(news_id=item_guid).exists():

                try:
                    item_pub_date_object = datetime.strptime(item_pubDate, pub_date_format)

                    fin_news = FinancialNews()
                    fin_news.news_id = item_guid
                    fin_news.symbol = f_symbol_inst
                    fin_news.description = item_description
                    fin_news.title = item_title
                    fin_news.link = item_link
                    fin_news.publish_date = item_pub_date_object
                    fin_news.save()
                except Exception as e:
                    logger_cl.error('Error in saving news item: %s' % (scraped_item,))
                    logger_cl.exception(e)

            else:
                logger_cl.debug('News already exist!')

        else:
            logger_cl.error('Error in saving news item: %s' % (scraped_item,))
