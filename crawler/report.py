""" class added for automatic report generation """


class Report:
    def __init__(self):
        self.unique_pages = 0
        self.longest_page = ['', 0]
        self.common_words = dict()
        self.sub_domains = dict()

    def update_unique(self, num_pages):
        self.unique_pages += num_pages

    def get_unique(self):
        return self.unique_pages

    def update_longest(self, new_longest_page):
        self.longest_page = new_longest_page
