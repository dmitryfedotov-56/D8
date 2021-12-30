import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')
from celery.schedules import crontab

app = Celery('news_project')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'action_every_30_seconds': {
        'tasks': 'tasks.hello',
        # 'schedule': 30,
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
        'args': (),
    },
}

