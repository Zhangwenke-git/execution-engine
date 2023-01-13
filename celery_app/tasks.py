import json
import os
import time
import traceback
import datetime
from celery_app import app
from config.settings import Settings
from tools.config_loader import conf
from testsuites.runner import pytest_exec
from tools.logger import logger
from tools.rabbitmq import amqp
from tools.ftp import _ftp
# from celery.utils.log import get_task_logger
# logger = get_task_logger(__name__)
from tools.redis_utils import redis_

redis = redis_()

@app.task(bind=True)
def celery_exec_operation(self, data):
    """
    此为异步任务
    执行用例，并将测试报告的附加信息写入attributes.txt文件中，供以后展示在测试报告中
    @param data:待执行的数据{"exec_id":XXXXXXX,"data":data}
    @return: 测试操作是否执行成功以及测试报告的结果
    """

    execID = data["exec_id"]
    response = {"exec_id": execID, "success": False, "path": "execution error", "duration": 0.00,
                'hostIp': conf("local.host.ip"), 'requestTime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    heart_beat = True if execID == "HEART_BEAT" else False


    try:
        logger.debug(('executing task id {0.id}, args: {0.args!r}, kwargs: {0.kwargs!r}').format(self.request))
        attributes = {"执行编码": data["exec_id"], "用例数": len(data["body"])}
        redis.set("attributes", json.dumps(attributes, ensure_ascii=False))
        pytest_obj = pytest_exec()
        is_success, message = pytest_obj.execute(execID, data["body"])
    except Exception:
        logger.error(f"pytest execution error due to {traceback.format_exc()}")
    else:
        if not heart_beat:
            remote_path = conf("report.remote.dir") + "/%s/%s/%s.html" % (
            time.strftime("%Y%m%d", time.localtime()), execID, execID)
            if is_success:
                redis.lpush("completed_exec_ids",execID)
                celery_upload_result = celery_upload(execID)  # 异步上传，不再等待
                if celery_upload_result:
                    response.update(success=True, path=remote_path, duration=message)
                else:
                    response.update(path="report upload failure")
            else:
                response.update(path=message)
            celery_response_send.delay(response)
        else:
            if is_success:
                response.update(success=True,path=None)
                logger.info(f"send HEART-BEAT message from pytest:{response}")
                celery_response_send.delay(response)
            else:
                logger.critical(f"HEART-BEAT error,please check it.")

def celery_upload(execID):
    """
    根据执行编码上传到FTP服务器上，并把execID作为报告的父目录
    @param execID:执行编码
    """
    success = False
    remote_path = os.path.join(conf("report.remote.dir"), "%s" % time.strftime("%Y%m%d", time.localtime()))
    try:
        ftp = _ftp()
        ftp.create_dir(r"%s" % time.strftime("%Y%m%d", time.localtime()))
        ftp.upload_folder(local_path=os.path.join(Settings.base_dir, "report/ant/%s/%s" % (
        time.strftime("%Y%m%d", time.localtime()), execID)), remote_path=remote_path)
        ftp.close()
    except Exception:
        logger.error(f"fail to upload report: {execID} due to error: {traceback.format_exc()}.")
    else:
        redis.lpush("report_exec_ids", execID)
        logger.info(f"upload report: {execID} successfully.")
        success = True
    return success


@app.task
def celery_response_send(response: dict):
    logger.info(f"reply message from pytest:{response}")
    mq = amqp(conf("mq.reply.queue"))
    mq.basic_publish(response, conf("mq.pytest.result.reply.routing.key"))
    logger.info(f"success to return execution result.")
