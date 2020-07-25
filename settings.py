from os.path import join, dirname
import os

__vhost = str(os.environ.get("RABBITMQ_VHOST"))
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "rabbitmq")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "rabbitmq")
RABBITMQ_VHOST = os.environ.get("RABBITMQ_VHOST", "/")
QUEUE_NAME_CONSUMER = os.environ.get("QUEUE_NAME_CONSUMER", "legacy-worker")
EXCHANGE_NAME = os.environ.get("EXCHANGE_NAME", "exc-worker")
CONSUME_ROUTING_KEY = os.environ.get("CONSUME_ROUTING_KEY", "legacy_import")
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "scheduler")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "jobs")
MONGO_PORT = os.environ.get("MONGO_PORT", 27017)
MONGO_USER = os.environ.get("MONGO_USER", "mongo")
MONGO_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "mongo")