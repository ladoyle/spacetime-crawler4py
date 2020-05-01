from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
from crawler.report import Report


class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory
        self.report = Report()

    def start_async(self):
        self.workers = [
            # gave a report reference to each thread
            self.worker_factory(worker_id, self.config, self.frontier, self.report)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()
        self.report.generate_report()

    def join(self):
        self.frontier.to_be_downloaded.join()
        for worker in self.workers:
            worker.join()
