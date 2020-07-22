from logzero import logger


class LegacyBaseImportWorker(object):
    def process(self):
        logger.info('Process have started!')
