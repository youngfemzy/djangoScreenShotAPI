# project_root/project/celery.py
import os
from celery import Celery

# set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'screenshot_generator.settings')

app = Celery('project')

# load settings from Django settings.py (CELERY_… variables)
app.config_from_object('django.conf:settings', namespace='CELERY')

# discover tasks.py files inside apps
app.autodiscover_tasks()
