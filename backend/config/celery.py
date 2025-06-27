import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.base")

app = Celery('core')
app.conf.timezone = "Europe/Moscow"

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
