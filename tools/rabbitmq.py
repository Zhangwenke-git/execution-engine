import json
import pika
from pika import exceptions
from retry import retry
from tools.config_loader import conf
from tools.logger import logger
from tools.set_single_instance import Singleton



class AMQP(metaclass=Singleton):

    def __init__(self, host, username, password, port, exchange, virtual_host="/", queue=""):
        self.host = host
        self.username = username
        self.password = password
        self.port = int(port)
        self.virtual_host = virtual_host
        self.exchange = exchange
        self.queue = queue
        self.EXCHANGE_TYPE = "topic"

    @property
    def _connect(self):
        credentials = pika.PlainCredentials(username=self.username, password=self.password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port,
                                                                            virtual_host=self.virtual_host,
                                                                            credentials=credentials, heartbeat=60,
                                                                            ))
        if self.connection is not None:
            logger.info(
                f"success to connect rabbitMQ with ({self.host, self.username, self.virtual_host, self.exchange, self.queue})")
            return self.connection

    @property
    def _channel(self):
        self.channel = self._connect.channel()
        self.channel.basic_qos(prefetch_count=1)
        return self.channel

    def _exchange(self):
        self._channel.exchange_declare(exchange=self.exchange, durable=True, exchange_type=self.EXCHANGE_TYPE)

    def _queue(self, queue):
        self.channel.queue_declare(queue=queue, durable=True)

    @retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
    def basic_publish(self, body, routing_key):
        self._exchange()
        if isinstance(body, (list, dict)):
            body = json.dumps(body)
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=body, properties=pika.BasicProperties(delivery_mode=2))
        logger.debug(f"publish message {body} to {self.exchange} by routing-key:{routing_key}")

    def basic_consume(self, routing_key, callback):
        self._exchange()
        result = self._channel.queue_declare(queue=self.queue, durable=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=self.exchange, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(
            queue=queue_name,
            auto_ack=False,
            on_message_callback=callback)

    @retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
    def consume(self, routing_key, callback):
        self.basic_consume(routing_key, callback)
        try:
            self.channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            ...

    def close(self):
        self.connection.close()


def amqp(queue, _class=AMQP):
    amqp_ = _class(host=conf("mq.host"),
                    username=conf("mq.user"),
                    password=conf("mq.password"),
                    port=conf("mq.port"),
                    exchange=conf("mq.exchange"),
                    virtual_host=conf("mq.virtual_host"),
                    queue=queue)
    return amqp_
