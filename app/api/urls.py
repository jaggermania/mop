from django.urls import path

from . import views

urlpatterns = [
    path('financial_news/<str:symbol>/', views.FinancialNewsList.as_view(), name='financial_news_list'),
]
