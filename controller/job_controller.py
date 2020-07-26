from worker.worker_scheduler import SchedulerJob


class JobController:
    def __init__(self):
        self.scheduler = SchedulerJob()

    def handle_package(self, package: dict, publish):
        if package.get('status_job').upper() == 'CREATE':
            self.scheduler.add_job_to_scheduler(package, publish)
        # if package.get('status_job').upper() == 'REMOVE':
        #     self.scheduler.remove_job_from_scheduler(package)
        # if package.get('status_job').upper() == 'CANCEL':
        #     self.scheduler.cancel_job_scheduler(package)
