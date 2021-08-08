# Generated by Django 3.2.6 on 2021-08-05 16:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('financial_news', '0002_auto_20210805_1501'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialNews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news_id', models.CharField(max_length=256, unique=True)),
                ('description', models.TextField()),
                ('title', models.TextField()),
                ('link', models.TextField()),
                ('publish_date', models.DateTimeField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('symbol',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='financial_symbol_news',
                                   to='financial_news.financialsymbol')),
            ],
            options={
                'db_table': 'financial_news',
            },
        ),
    ]
