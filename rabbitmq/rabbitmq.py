import json
import pika
from logzero import logger
from pika.exceptions import ChannelClosed, ConnectionClosed
from controller.job_controller import JobController
import settings


class RabbitMQClient(object):
    _conn = None
    _channel = None

    def __init__(self):
        self.host = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.username = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASSWORD
        self.vhost = settings.RABBITMQ_VHOST
        self.queue = settings.QUEUE_NAME_CONSUMER
        self.exchange = settings.EXCHANGE_NAME
        self.consume_routing_key = settings.CONSUME_ROUTING_KEY
        self.job_controller = JobController()

    @property
    def credentials(self) -> pika.PlainCredentials:
        return pika.PlainCredentials(self.username, self.password)

    @property
    def connection_parameters(self) -> pika.ConnectionParameters:
        return pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.vhost,
            credentials=self.credentials,
            heartbeat=180,
        )

    def _get_connection(self, params):
        try:
            if RabbitMQClient._conn:
                self._conn = RabbitMQClient._conn
            else:
                self._conn = RabbitMQClient._conn = pika.BlockingConnection(
                    params)
                logger.info(
                    f"RabbitMQ --->> New connection in {self.host}:{self.port}")
        except Exception as ex:
            logger.warning(f"RabbitMQ --->> Failed connection {ex}")

    @property
    def conn(self) -> pika.BlockingConnection:
        if self._conn is None:
            self._get_connection(self.connection_parameters)

        return self._conn

    def _get_channel(self):
        if RabbitMQClient._channel:
            self._channel = RabbitMQClient._channel
        else:
            self._channel = RabbitMQClient._channel = self.conn.channel()

    def _configure_channel(self):
        self._channel.basic_qos(prefetch_count=1)
        self._channel.queue_declare(
            queue=self.queue,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

        self._channel.queue_bind(
            exchange=self.exchange,
            queue=self.queue,
            routing_key=self.consume_routing_key
        )

    @property
    def channel(self):
        if self._channel is None:
            self._get_channel()
            self._configure_channel()

        return self._channel

    def _stop_channel(self):
        self.channel.stop_consuming()
        RabbitMQClient._channel = None
        logger.info(
            "RabbitMQ --->> Sending a basic.cancel rpc command to rabbitmq")

    def _stop_connection(self):
        self.conn.close()
        RabbitMQClient._conn = None
        logger.info("RabbitMQ --->> Connection closed")

    def stop(self):
        self._stop_channel()
        self._stop_connection()

    def reconnect(self):
        logger.error(f"RabbitMQ: Reconnecting...")
        self.stop()
        self.run()

    def run(self):
        try:
            logger.info(f"RabbitMQ --->> Consuming queue {self.queue}")
            self.channel.basic_consume(self.handle_delivery, queue=self.queue)
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop()

    def handle_delivery(self, channel, method, properties, body):
        data = json.loads(body.decode("utf-8"))
        try:
            self.job_controller.handle_package(data)
            channel.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
            # if response:
            #     self.publish(exchange=settings.EXCHANGE_NAME, routing_key=settings.PUBLISH_ROUTING_KEY,
            #                  message=response)
            #     channel.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
            # else:
            #     self.on_search_fail(properties, data)
            #     channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        except ChannelClosed:
            self.reconnect()

        except ConnectionClosed:
            self.reconnect()

        except Exception as ex:
            logger.error(f"RabbitMQ --->> Failed to handle message: {ex} - {data}")
            raise ex

    def on_search_fail(self, properties, data):
        try:
            properties.headers[settings.RETRY_COUNTER_HEADER_NAME] += 1
            if properties.headers[settings.RETRY_COUNTER_HEADER_NAME] < settings.MESSAGE_PROCESSING_MAX_ATTEMPTS:
                self.publish(exchange=settings.EXCHANGE_NAME, routing_key=settings.CONSUME_ROUTING_KEY, message=data,
                             properties=properties)
        except TypeError:
            properties.headers = {settings.RETRY_COUNTER_HEADER_NAME: 1}
            self.publish(exchange=settings.EXCHANGE_NAME, routing_key=settings.CONSUME_ROUTING_KEY, message=data,
                         properties=properties)

        except KeyError:
            properties.headers[settings.RETRY_COUNTER_HEADER_NAME] = 1
            self.publish(exchange=settings.EXCHANGE_NAME, routing_key=settings.CONSUME_ROUTING_KEY, message=data,
                         properties=properties)

    def publish(self, exchange: str, routing_key: str, message: dict, properties=None):
        logger.info(f"TO QUEUE --->> {routing_key} | PACKAGE SENDED --->> {message}")
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(message),
                                   properties=properties)
