import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db.utils import OperationalError
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    """Command for initial custom django setup"""

    def handle(self, *args, **options):
        self.__create_super_user()
        self.__configure_celery_beat()

    def __create_super_user(self):
        """Method for creating superuser"""
        self.stdout.write('Creating superuser ...')
        try:
            User = get_user_model()
            if not User.objects.filter(username=os.environ.get('DJANGO_SUPERUSER_USERNAME')).exists():
                superuser = User.objects.create_superuser(username=os.environ.get('DJANGO_SUPERUSER_USERNAME'),
                                                          email=os.environ.get('DJANGO_SUPERUSER_EMAIL'),
                                                          password=os.environ.get('DJANGO_SUPERUSER_PASSWORD'))
                superuser.save()
                self.stdout.write(self.style.SUCCESS('Superuser created!'))
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        'User %s already exist, skipping.' % (os.environ.get('DJANGO_SUPERUSER_USERNAME'),)))

        except OperationalError:
            self.stdout.write('Error in creating superuser!')

    def __configure_celery_beat(self):
        """Method for django-celery-beat initial configuration"""
        self.stdout.write('Configuring django-celery-beat ...')
        try:
            schedule, created_interval = IntervalSchedule.objects.get_or_create(every=10,
                                                                                period=IntervalSchedule.MINUTES)
            task, created_task = PeriodicTask.objects.get_or_create(interval=schedule, name='Scraping news',
                                                                    task='financial_news.tasks.scraping_task')
            if created_task:
                self.stdout.write(self.style.SUCCESS('Configuration finished!'))
            else:
                self.stdout.write(self.style.SUCCESS('Already configured, skipping.'))
        except OperationalError:
            self.stdout.write(self.style.SUCCESS('Error in configuring django-celery-beat!'))
