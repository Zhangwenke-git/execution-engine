import json
import traceback
from tools.color import Color
from tools.rabbitmq import amqp
from tools.config_loader import conf
import multiprocessing
from loguru import logger
from lib.core.cleaner import Cleaner
from celery.result import AsyncResult
from celery_app.tasks import celery_exec_operation



def callback(ch, method, props, body):
    """
    RPC的MQ连接方式，并将后台处理的结果返回
    @param ch:
    @param method:
    @param props:
    @param body:
    """
    message =json.loads(body)
    try:
        logger.info(f"send task EXEC_ID:{message.get('exec_id')} to pytest engine.")
        celery_exec_operation.delay(message)
    except Exception:
        logger.error(f"process message from producer failed, due to error:{traceback.format_exc()}")
    else:
        logger.info(f"message consumption success.")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def pytest_consume():
    mq_request = amqp(queue=conf("mq.request.queue"))
    mq_request.consume(routing_key="#.exec.#", callback=callback)

def server():
    """
    启动MQ的后台监听服务，消费消息，处理消息，将处理结果返回生产者
    多进程消费
    """
    try:
        pytest_consume()
    except Exception:
        logger.error(f'fail to start case execution engine,error as followings:{traceback.format_exc()}')
    else:
        Color.green('=======================================Success to launch case execution engine=======================================')
        Cleaner.clean_module_file()
        Cleaner.clean_report_file()
        Cleaner.clear_template_file()
        logger.info(f'success to launch case execution engine')

