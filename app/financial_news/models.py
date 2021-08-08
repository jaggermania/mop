from django.db import models


class FinancialSymbol(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.TextField()
    scraping_on = models.BooleanField(default=True)

    class Meta:
        db_table = 'financial_symbol'

    def __str__(self):
        return self.symbol


class FinancialNews(models.Model):
    news_id = models.CharField(max_length=256, unique=True)
    symbol = models.ForeignKey(FinancialSymbol, on_delete=models.CASCADE, related_name="financial_symbol_news")
    description = models.TextField()
    title = models.TextField()
    link = models.TextField()

    publish_date = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'financial_news'

    def __str__(self):
        return self.news_id
