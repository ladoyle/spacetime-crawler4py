import time
from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, report):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.report = report
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler")
                break
            self.report.lock_domain(tbd_url)
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            # passed the report reference to the scraper for updating
            scraped_urls = scraper(tbd_url, resp, self.frontier.save, self.report)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
            self.report.release_domain(tbd_url)
