from logzero import logger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_ADDED, EVENT_JOB_SUBMITTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from datetime import datetime, timedelta
from pymongo import MongoClient
from func_timeout import func_set_timeout, FunctionTimedOut
import time

from helpers.job import Job
from helpers.worker_constants import WorkerConstants
from worker.worker_legacy_base_import import LegacyBaseImportWorker
from worker.worker_listener import job_status_listener
import settings


class SchedulerJob:
    def __init__(self):
        self.publish = None
        client = MongoClient(
            host='localhost',
            username='root',
            password='KXZBE5PRfO',
            port=27017,
            authSource="admin"
        )
        self.client_mongo = client
        self.scheduler = BackgroundScheduler()
        self.jobstore = MongoDBJobStore(database='scheduler', collection='jobs', client=self.client_mongo)
        self.scheduler.add_jobstore(jobstore=self.jobstore)
        self.worker = LegacyBaseImportWorker()

    def add_job_to_scheduler(self, data: dict, publish):
        self.publish = publish
        # start_date = datetime.now() + timedelta(seconds=30)
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
        id_job = data.get('id_job')
        self.scheduler.add_job(id=id_job, func=self.worker.process, name='date', run_date=start_date,
                               args=[id_job])
        self.scheduler.add_listener(self.job_status_listener_local,
                                    EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_ADDED |
                                    EVENT_JOB_SUBMITTED)
        logger.info(f'Job created: {id_job}')
        self.run()

    def remove_job_from_scheduler(self, data: dict):
        id_job = data.get('id_job')
        try:
            self.scheduler.remove_job(id_job)
            logger.info(f'Job removed: {id_job}')
        except Exception as e:
            logger.error(f"Error removing job {e}")
        self.run()

    def cancel_job_scheduler(self, data: dict):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info('Scheduler was shutdown')
        self.remove_job_from_scheduler(data)
        self.run()

    def run(self):
        try:
            logger.info("Worker scheduler running")
            self.scheduler.start()
            self.scheduler.print_jobs()
        except:
            pass

    def job_status_listener_local(self, event):
        constants = WorkerConstants()
        job_id = event.job_id
        if hasattr(event, 'exception') and event.exception:
            if isinstance(event.exception, FunctionTimedOut):
                job = Job(id_job=job_id, status_job=constants.TIMEDOUT)
                logger.error(f"Job {job_id} crashed due timeout")
            else:
                job = Job(id_job=job_id, status_job=constants.ERROR)
                logger.error(f"Job {job_id} crashed due {str(event.exception)}")
        else:
            if event.code == constants.CREATED_JOB_CODE:
                job = Job(id_job=job_id, status_job=constants.CREATE)
            elif event.code == constants.RUNNING_JOB_CODE:
                job = Job(id_job=job_id, status_job=constants.RUNNING)
            else:
                job = Job(id_job=job_id, status_job=constants.FINISHED)
        self.publish(exchange="", routing_key=settings.QUEUE_NAME_PUBLISHER, message=job._asdict())