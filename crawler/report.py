""" class added for automatic report generation """
import sys
import time
from threading import RLock

from crawler.hasher import SimHash


def to_seconds(full_time):
    return 3600*full_time.tm_hour + 60*full_time.tm_min + full_time.tm_sec


class Report:
    def __init__(self):
        self.lock = RLock()
        self.simhash = SimHash()
        self.unique_pages = 0
        self.longest_page = ('', 0)
        self.common_words = dict()
        self.sub_domains = dict()

        current_time = to_seconds(time.localtime())
        self.domain_times = {
            'ics.uci.edu': current_time,
            'cs.uci.edu': current_time,
            'informatics.uci.edu': current_time,
            'stat.uci.edu': current_time,
            'today.uci.edu': current_time
        }

    def update_unique(self, num_pages):
        self.lock.acquire()
        self.unique_pages += num_pages
        self.lock.release()

    def get_unique(self):
        return self.unique_pages

    def update_longest(self, new_longest_page):
        self.lock.acquire()
        self.longest_page = new_longest_page
        self.lock.release()

    def get_longest(self):
        return self.longest_page[0]

    def update_common(self, new_words):
        self.lock.acquire()
        for word in new_words:
            if self.common_words.get(word):
                self.common_words[word] += new_words[word]
            else:
                self.common_words[word] = new_words[word]
        self.lock.release()

    def get_common(self):
        fifty_words = sorted(self.common_words.items(),
                             key=lambda x: x[:1],
                             reverse=True)
        if len(fifty_words) >= 50:
            fifty_words = fifty_words[:50]
        word_list = ''
        i = 1
        for word, freq in fifty_words:
            word_list += f'\t{i}) {word} -> {freq}\n'
            i += 1
        return word_list

    def update_domains(self, domains):
        self.lock.acquire()
        for domain in domains:
            self.sub_domains[domain] = domains[domain]
        self.lock.release()

    def get_domains(self):
        domains = sorted(self.sub_domains.items())
        dom_list = ''
        i = 1
        for dom, freq in domains:
            dom_list += f'\t{i}) {dom} -> {freq}\n'
            i += 1
        return dom_list

    def check_is_recent(self, url, current_time):
        time_seconds = to_seconds(current_time)
        for domain in self.domain_times:
            recent = time_seconds - self.domain_times[domain]
            if url.find(domain) != -1 and recent < 0.5:
                return True
        return False

    def update_recent_time(self, url):
        self.lock.acquire()
        for domain in self.domain_times:
            if url.find(domain) != -1:
                self.domain_times[domain] = to_seconds(time.localtime())
                break
        self.lock.release()

    def generate_report(self):
        try:
            with open("hw2_report.txt", 'w') as report_file:
                report_file.write(f'Unique pages found:\t{self.get_unique()}\n'
                                  f'Longest page by words:\t{self.get_longest()}\f'
                                  f'50 most common words:\n{self.get_common()}\f'
                                  f'Sub-domains for ics.uci.edu:\n{self.get_domains()}')
        except IOError:
            print("Report Error: could not write to hw2_report.txt file", file=sys.stderr)
