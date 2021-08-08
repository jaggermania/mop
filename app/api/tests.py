import datetime
import json

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from financial_news.models import FinancialNews
from financial_news.tasks import fetch_financial_news_by_url, save_to_db_scraped_financial_news_for_symbol

client = Client()


class ApiTestCase(TestCase):
    fetch_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    fetch_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US"

    def setUp(self):
        symbol = "INTC"
        scraped_news = fetch_financial_news_by_url(self.fetch_url % (symbol,), self.fetch_headers)
        save_to_db_scraped_financial_news_for_symbol(symbol, scraped_news)

    def test_get_basic_request(self):
        bad_symbol = "INTC_1234"
        good_symbol = "INTC"

        """ 1. Bad symbol request """
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': bad_symbol}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        """ 2. Good symbol request """
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': good_symbol}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        """ 3. Request without symbol """
        response = client.get("/api/financial_news//")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_paging_request(self):
        symbol = "INTC"

        """ 1. Request of first page """
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': symbol}), params={'page': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 20)

        """ 2. Request of not existing page """
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': symbol}), {'page': '555'})
        self.assertEqual(json.loads(response.content)["detail"], "Invalid page.")

    def test_get_filtering_request(self):
        symbol = "INTC"
        last_news = FinancialNews.objects.filter().last()
        publish_date_format = '%Y-%m-%d'

        """ 1. Filter by existing news ID """
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': symbol}),
            {'news_id': last_news.news_id})
        self.assertEqual(response.data['count'], 1)

        """ 2. Filter by not existing news ID """
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': symbol}),
            {'news_id': "bad news id"})
        self.assertEqual(response.data['count'], 0)

        """ 3. Filter by description """
        description_test = 'Intel'
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': symbol}),
            {'description': description_test})
        self.assertEqual(response.data['count'], FinancialNews.objects.filter(symbol__symbol=symbol,
                                                                              description__contains=description_test).count())

        """ 4. Filter by title """
        title_test = 'Intel'
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': symbol}),
            {'title': title_test})
        self.assertEqual(response.data['count'], FinancialNews.objects.filter(symbol__symbol=symbol,
                                                                              title__contains=title_test).count())

        """ 5. Filter by publish_date_before and publish_date_after """
        test_date_period_start = last_news.publish_date + datetime.timedelta(days=-10)
        test_date_period_end = last_news.publish_date + datetime.timedelta(days=10)

        """ When publish_date_before > publish_date_after """
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': symbol}),
            {'publish_date_after': test_date_period_start.strftime(publish_date_format),
             'publish_date_before': test_date_period_end.strftime(publish_date_format)})
        self.assertEqual(response.data['count'],
                         FinancialNews.objects.filter(symbol__symbol=symbol, publish_date__gte=test_date_period_start,
                                                      publish_date__lte=test_date_period_end).count())

        """ When publish_date_before < publish_date_after """
        response = client.get(
            reverse('financial_news_list', kwargs={'symbol': symbol}),
            {'publish_date_after': test_date_period_end.strftime(publish_date_format),
             'publish_date_before': test_date_period_start.strftime(publish_date_format)})
        self.assertEqual(response.data['count'], 0)
