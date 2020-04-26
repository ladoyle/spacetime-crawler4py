""" class added for automatic report generation """


class Report:
    def __init__(self):
        self.unique_pages = 0
        self.longest_page = ('', 0)
        self.common_words = dict()
        self.sub_domains = dict()

    def update_unique(self, num_pages):
        self.unique_pages += num_pages

    def get_unique(self):
        return self.unique_pages

    def update_longest(self, new_longest_page):
        self.longest_page = new_longest_page

    def get_longest(self):
        return self.longest_page

    def update_common(self, new_words):
        for word, freq in new_words:
            if self.common_words.get(word):
                self.common_words[word] += freq
            else:
                self.common_words[word] = freq

    def get_common(self):
        return self.common_words

    def update_domains(self, domains):
        for domain, freq in domains:
            self.sub_domains[domain] = freq