from logzero import logger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from datetime import datetime, timedelta
from pymongo import MongoClient


class SchedulerJob:
    def __init__(self):
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
        self.scheduler.add_listener(self.job_status_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    @staticmethod
    def job_status_listener(event):
        if event.exception:
            print('The job crashed :(')
        else:
            print('The job worked :)')

    def add_job_to_scheduler(self, data: dict):
        trigger_on = datetime.now() + timedelta(seconds=5)
        self.scheduler.add_job(id=data.get('id'), func=do_it, name='date', run_date=trigger_on)
        logger.info('Task created')
        self.run()

    def run(self):
        try:
            logger.info("Worker scheduler running")
            self.scheduler.start()
        except:
            pass


def do_it():
    logger.info('Doing task')
