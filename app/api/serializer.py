from rest_framework import serializers

from financial_news.models import FinancialNews


class FinancialNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialNews
        fields = ['news_id', 'description', 'link', 'title', 'publish_date']
