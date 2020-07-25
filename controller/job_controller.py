from worker.worker_scheduler import SchedulerJob


class JobController:
    def __init__(self):
        self.scheduler = SchedulerJob()

    def handle_package(self, package: dict):
        if package.get('status_job').upper() == 'CREATE':
            self.scheduler.add_job_to_scheduler(package)
