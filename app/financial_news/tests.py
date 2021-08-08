from django.test import TestCase

from financial_news.models import FinancialNews, FinancialSymbol
from financial_news.tasks import get_scraping_symbols, fetch_financial_news_by_url, \
    save_to_db_scraped_financial_news_for_symbol


class ScrapingTestCase(TestCase):
    fetch_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    fetch_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US"

    def test_get_scraping_symbols(self):
        """Collect scraping symbols from DB"""
        self.assertEqual(get_scraping_symbols(), ['AAPL', 'TWTR', 'GC=F', 'INTC'])

    def test_fetch_financial_news_by_url(self):
        """Fetch news"""
        bad_symbol = "INTC_1234"
        good_symbol = "INTC"

        self.assertEqual(fetch_financial_news_by_url(self.fetch_url % (bad_symbol,), self.fetch_headers), [])
        self.assertEqual(fetch_financial_news_by_url(self.fetch_url % (bad_symbol,), {}), False)

        fetch_data_ok = fetch_financial_news_by_url(self.fetch_url % (good_symbol,), self.fetch_headers)
        self.assertEqual(True if isinstance(fetch_data_ok, list) and len(fetch_data_ok) else False, True)

    def test_save_to_db_scraped_financial_news_for_symbol(self):
        """Save fetched records to db"""
        symbol = "INTC"

        scraped_news = fetch_financial_news_by_url(self.fetch_url % (symbol,), self.fetch_headers)

        FinancialNews.objects.all().delete()
        save_to_db_scraped_financial_news_for_symbol(symbol, scraped_news)

        self.assertEqual(FinancialNews.objects.all().count(), len(scraped_news))
