from datetime import timedelta
from celery.schedules import crontab  # crontab(hour=15, minute=0) crontab(hour=6, minute=0)
from tools.config_loader import conf


# broker_url = 'amqp://admin:aaaa1111!@192.168.44.129:5672//'
broker_url = f'amqp://{conf("mq.user")}:{conf("mq.password")}@{conf("mq.host")}:{int(conf("mq.port"))}//'

# result_backend = 'redis://192.168.44.129:6379/1'
result_backend = f'redis://{conf("redis.host")}:{int(conf("redis.port"))}/{int(conf("celery.result.backend.db"))}'

timezone = 'Asia/Shanghai'
enable_utc = False

beat_schedule = {
    'heart_beats_job': {
        'task': 'celery_app.jobs.heart_beats',
        'schedule': timedelta(seconds=int(conf("heart.beats.job.timedelta"))),
        'args': ()
    },
    'clean_logs_job': {
        'task': 'celery_app.jobs.clean_logs_job',
        'schedule': crontab(hour=int(conf("clean.logs.job.hour")), minute=int(conf("clean.logs.job.minute"))),
        'args': (7,)
    },
    'clean_module_job': {
        'task': 'celery_app.jobs.clean_module_job',
        'schedule': timedelta(seconds=int(conf("clean.module.job.timedelta"))),
        'args': ()
    },
    'clean_report_job': {
        'task': 'celery_app.jobs.clean_report_job',
        'schedule': timedelta(seconds=int(conf("clean.report.job.timedelta"))),
        'args': ()
    },
}

