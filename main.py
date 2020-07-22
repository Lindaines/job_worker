import threading
from worker.worker_scheduler import SchedulerJob
from rabbitmq.rabbitmq import RabbitMQClient


def main():
    threading.Thread(target=SchedulerJob().run()).start()
    threading.Thread(target=RabbitMQClient().run()).start()


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
