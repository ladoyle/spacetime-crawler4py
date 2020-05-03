""" class added for automatic report generation """
import sys
from threading import RLock

from crawler.hasher import SimHash


def to_milli(full_time):
    return int(round(full_time * 1000))


class Report:
    def __init__(self):
        self.lock_report = RLock()
        self.simhash = SimHash()
        self.unique_pages = 0
        self.longest_page = ('', 0)
        self.common_words = dict()
        self.sub_domains = dict()

        self.scraped_domains = [
            '.ics.uci.edu',
            '.cs.uci.edu',
            '.informatics.uci.edu',
            '.stat.uci.edu',
            'today.uci.edu'
        ]
        self.domain_locks = []
        for i in range(5):
            self.domain_locks.append(RLock())

    def update_unique(self, num_pages):
        self.lock_report.acquire()
        self.unique_pages += num_pages
        self.lock_report.release()

    def update_longest(self, new_longest_page):
        self.lock_report.acquire()
        self.longest_page = new_longest_page
        self.lock_report.release()

    def update_common(self, new_words):
        self.lock_report.acquire()
        for word in new_words:
            if self.common_words.get(word):
                self.common_words[word] += new_words[word]
            else:
                self.common_words[word] = new_words[word]
        self.lock_report.release()

    def write_common_words(self, file):
        fifty_words = sorted(self.common_words.items(),
                             key=lambda x: x[:1],
                             reverse=True)
        if len(fifty_words) >= 50:
            fifty_words = fifty_words[:50]
        i = 1
        file.write("50 most common words:\n")
        for word, freq in fifty_words:
            if type(word) is bytes:
                word = word.decode()
            file.write("\t{}) {} -> {}\n".format(i, word, freq))
            i += 1
        file.write("\n\n\n")

    def update_domains(self, domains):
        self.lock_report.acquire()
        for domain in domains:
            self.sub_domains[domain] = domains[domain]
        self.lock_report.release()

    def write_domains(self, file):
        domains = sorted(self.sub_domains.items())
        i = 1
        file.write("Sub-domains for ics.uci.edu:\n")
        for dom, freq in domains:
            if type(dom) is bytes:
                dom = dom.decode()
            file.write("\t{}) {} -> {}\n".format(i, dom, freq))
            i += 1

    def lock_domain(self, url):
        i = 0
        for domain in self.scraped_domains:
            if url.find(domain) != -1:
                self.domain_locks[i].acquire()
                break
            i += 1

    def release_domain(self, url):
        i = 0
        for domain in self.scraped_domains:
            if url.find(domain) != -1:
                self.domain_locks[i].release()
                break
            i += 1

    def generate_report(self):
        try:
            with open("hw2_report.txt", 'w') as report_file:
                report_file.write("Unique pages found:\t" + str(self.unique_pages) + "\n")
                report_file.write("Longest page by words:\n\t"
                                  + str(self.longest_page[0]) + "\n\t" + str(self.longest_page[1])
                                  + "\n\n\n")
                self.write_common_words(report_file)
                self.write_domains(report_file)
        except IOError:
            print("Report Error: could not write to hw2_report.txt file", file=sys.stderr)
