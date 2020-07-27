from func_timeout import func_set_timeout
from logzero import logger
import time
import settings


class LegacyBaseImportWorker(object):

    @func_set_timeout(timeout=settings.TIMEOUT_IN_SECONDS)
    def process(self, id_job):
        logger.info(f'Doing task {id_job}')
        time.sleep(settings.FAKE_PROCESS_TIME_IN_SECONDS)
        logger.info(f'Done task {id_job}')
