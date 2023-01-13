import os
import logging.config
from tools.config_loader import conf
from datetime import datetime
from config.settings import Settings


standard_format = '[%(asctime)s] [%(levelname)s] [%(threadName)s] [%(name)s] | %(message)s'
simple_format = '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] | %(message)s'

logfile_dir = os.path.join(Settings.base_dir, 'log')
logfile_name = 'log{0}.log'.format(datetime.now().strftime('%Y-%m-%d'))
os.makedirs(logfile_dir) if not os.path.isdir(logfile_dir) else ...
logfile_path = os.path.join(logfile_dir, logfile_name)


LOGGING_DIC = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': standard_format
        },
        'simple': {
            'format': simple_format
        },
    },
    'filters': {},  # filter可以不定义
    'handlers': {
        # 打印到终端的日志
        'console': {
            'level': conf.get("terminal.level"),
            'class': 'logging.StreamHandler',  # 打印到屏幕
            'formatter': 'simple'
        },
        # 打印到文件的日志,收集info及以上的日志
        'default': {
            'level': conf.get("logger.level"),
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': logfile_path,
            'maxBytes': 1024 * 1024 * 100,  # 日志大小100M  (*****)
            'backupCount': 5,
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'console'],
            'level': conf.get("logger.level").upper(),
            'propagate': False,  # 向上（更高level的logger）传递
        },
    },
}


logging.config.dictConfig(LOGGING_DIC)  # 导入上面定义的logging配置
logger = logging.getLogger(__name__)  # 生成一个log实例


