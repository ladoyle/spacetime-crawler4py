import sys
from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time


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
                self.logger.info("Frontier is empty. Stopping Crawler.")
                self.generate_report()
                break
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

    # added method to generate report
    def generate_report(self):
        try:
            with open("hw2_report.txt", 'w') as report_file:
                report_file.write(f'Unique pages found:\t{self.report.get_unique()}\n'
                                  f'Longest page by words:\t{self.report.get_longest()}\f'
                                  f'50 most common words:\n{self.report.get_common()}\f'
                                  f'Sub-domains for ics.uci.edu:\n{self.report.get_domains()}')
        except IOError:
            print("Report Error: could not write to hw2_report.txt file", file=sys.stderr)
