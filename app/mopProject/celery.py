import logging
import os
from logging.handlers import RotatingFileHandler

from celery import Celery
from celery.signals import after_setup_task_logger, after_setup_logger

# Set the default Django settings module for the 'celery' program.
from mopProject.settings import CELERY_LOG_FILE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mopProject.settings')

app = Celery('app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


def create_celery_logger_handler(logger, propagate):
    celery_handler = RotatingFileHandler(CELERY_LOG_FILE, maxBytes=209715200, backupCount=10)
    celery_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    celery_handler.setFormatter(celery_formatter)

    logger.addHandler(celery_handler)
    logger.logLevel = 'DEBUG'
    logger.propagate = propagate


@after_setup_task_logger.connect
def after_setup_celery_task_logger(logger, **kwargs):
    """ This function sets the 'celery.task' logger handler and formatter """
    create_celery_logger_handler(logger, False)


@after_setup_logger.connect
def after_setup_celery_logger(logger, **kwargs):
    """ This function sets the 'celery' logger handler and formatter """
    create_celery_logger_handler(logger, False)
