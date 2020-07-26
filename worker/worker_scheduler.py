from logzero import logger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_ADDED, EVENT_JOB_SUBMITTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
import time
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

    @staticmethod
    def job_status_listener(event):
        print(event)
        # if event.exception:
        #     print('The job crashed :(')
        # else:
        #     print('The job worked :)')

    def add_job_to_scheduler(self, data: dict):
        start_date = datetime.now() + timedelta(seconds=15)
        # start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
        id_job = data.get('id_job')
        self.scheduler.add_job(id=id_job, func=do_it, name='date', run_date=start_date,
                               args=[id_job])
        self.scheduler.add_listener(self.job_status_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_ADDED |
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


def do_it(id_job: str):
    logger.info(f'Doing task {id_job}')
    time.sleep(20)
    logger.info(f'Done task {id_job}')
