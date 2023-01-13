import os
import sys
from celery import Celery

BASE_DIRS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIRS)

app = Celery('Execution-Engine')

app.conf.timezone = 'Asia/Shanghai'

app.conf.enable_utc = False

app.config_from_object('config.celery_config')

app.autodiscover_tasks(packages=['celery_app'])

app.conf['imports'] = ['celery_app.tasks','celery_app.jobs',]
