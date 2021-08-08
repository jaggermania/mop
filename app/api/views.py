from datetime import datetime

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer

from api.serializer import FinancialNewsSerializer
from financial_news.models import FinancialNews


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class FinancialNewsList(generics.ListAPIView):
    serializer_class = FinancialNewsSerializer
    renderer_classes = [JSONRenderer]
    pagination_class = LargeResultsSetPagination
    __date_format = '%Y-%m-%d'
    __ordering_fields = ('news_id', 'description', 'title', 'publish_date')

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        symbol = self.kwargs['symbol']
        queryset = FinancialNews.objects.filter(symbol__symbol=symbol)

        queryset = self.apply_queryset_filters(queryset)
        queryset = self.apply_queryset_ordering(queryset)

        return queryset

    def apply_queryset_filters(self, queryset):
        queryset_filter = self._get_queryset_filters()
        return queryset.filter(**queryset_filter)

    def _get_queryset_filters(self):
        filters = {}

        news_id = self.request.query_params.get('news_id')
        description = self.request.query_params.get('description')
        title = self.request.query_params.get('title')
        publish_date_after = self.request.query_params.get('publish_date_after')
        publish_date_before = self.request.query_params.get('publish_date_before')

        if news_id is not None:
            filters['news_id'] = news_id

        if description is not None:
            filters['description__contains'] = description

        if title is not None:
            filters['title__contains'] = title

        if publish_date_after is not None:
            filters['publish_date__gte'] = publish_date_after
            try:
                _ = datetime.strptime(publish_date_after, self.__date_format)
            except Exception:
                raise ValidationError({'publish_date_after': 'Must be in following format YYYY-MM-DD'})

        if publish_date_before is not None:
            filters['publish_date__lte'] = publish_date_before
            try:
                _ = datetime.strptime(publish_date_before, self.__date_format)
            except Exception:
                raise ValidationError({'publish_date_before': 'Must be in following format YYYY-MM-DD'})

        return filters

    def apply_queryset_ordering(self, queryset):
        ordering = self._get_queryset_ordering()
        if ordering:
            return queryset.order_by(ordering)
        return queryset

    def _get_queryset_ordering(self):
        err_msg = {
            'ordering': 'API support ordering by %s. For descending order type \'-\' in front of ordering value like \'-title\'.'
                        % (self.__ordering_fields,)
        }

        ordering = self.request.query_params.get('ordering')

        if ordering is not None:
            if len(ordering):
                is_desc_ordering = True if ordering[0] == '-' else False
                ordering_str_chck = ordering[1:] if is_desc_ordering else ordering

                if ordering_str_chck not in self.__ordering_fields:
                    raise ValidationError(err_msg)

            else:
                raise ValidationError(err_msg)

        return ordering
