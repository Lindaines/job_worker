#from rabbitmq import rabbitmq
from logzero import logger
from helpers.job import Job
from helpers.worker_constants import WorkerConstants

import settings


def job_status_listener(event):
    constants = WorkerConstants()
    if hasattr(event, 'exception'):
        if event.exception:
            logger.error("Job crashed")
            job = Job(id_job='123', status_job=constants.ERROR)._asdict
            #rabbitmq.RabbitMQClient.publish(routing_key=settings.QUEUE_NAME_PUBLISHER, message=job)
