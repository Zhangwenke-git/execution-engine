import datetime
import os
import shutil
import time
from celery_app import app
from config.settings import Settings
from tools.logger import logger
from config.heat_beats_request import sample
from celery_app.tasks import celery_exec_operation
from tools.redis_utils import redis_

redis = redis_()

@app.task
def heart_beats():
    celery_exec_operation.delay(sample)

@app.task
def clean_module_job():
    """
    清理生成的module文件
    """
    completed_exec_ids = redis.lrange("completed_exec_ids",0,-1)
    suit_file_list = os.listdir(Settings.suit_dir)
    for f in suit_file_list:
        if f in completed_exec_ids:
            filepath = os.path.join(Settings.suit_dir, f)
            if os.path.isfile(filepath):
                os.remove(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath, True)

    redis.delete("completed_exec_ids")  # 定时任务执行完毕之后，重置已完成的信息
    logger.info(f"clear module py file job finished.")


@app.task
def clean_report_job():
    """
    清理生成的report文件
    """
    report_exec_ids = redis.lrange("report_exec_ids",0,-1)
    try:
        report_list = os.listdir(os.path.join(Settings.base_dir,
                                              "report/ant/%s" % time.strftime("%Y%m%d", time.localtime())))
        for f in report_list:
            if f in report_exec_ids:
                filepath = os.path.join(os.path.join(Settings.base_dir,
                                                     "report/ant/%s" % time.strftime("%Y%m%d", time.localtime())), f)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath, True)
    except FileExistsError:
        ...
    except FileNotFoundError:
        ...
    redis.delete("report_exec_ids")  # 定时任务执行完毕之后，重置已完成的信息
    logger.info(f"clear report htmls job finished.")


@app.task
def clean_logs_job(n):
    """
    清理生成的log文件
    """
    for root, dirs, files in os.walk(Settings.log_path):
        for file in files:
            full_name = os.path.join(root, file)
            create_time = int(os.path.getctime(full_name))
            delta_days = (datetime.datetime.now() - datetime.timedelta(days=n))
            time_stamp = int(time.mktime(delta_days.timetuple()))
            if create_time < time_stamp:
                os.remove(full_name)
    logger.info(f"clear log files job finished.")
