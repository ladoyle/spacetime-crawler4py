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
        return self.longest_page[0]

    def update_common(self, new_words):
        for word in new_words:
            if self.common_words.get(word):
                self.common_words[word] += new_words[word]
            else:
                self.common_words[word] = new_words[word]

    def get_common(self):
        fifty_words = sorted(self.common_words.items(),
                             key=lambda x: x[:1],
                             reverse=True)
        if len(fifty_words) >= 50:
            fifty_words = fifty_words[:50]
        word_list = ''
        i = 1
        for word, freq in fifty_words:
            word_list.join(f'\t{i}) {word} -> {freq}\n')
            i += 1
        return word_list

    def update_domains(self, domains):
        for domain in domains:
            self.sub_domains[domain] = domains[domain]

    def get_domains(self):
        domains = sorted(self.sub_domains.items())
        dom_list = ''
        i = 1
        for dom, freq in domains:
            dom_list.join(f'\t{i}) {dom} -> {freq}\n')
            i += 1
        return dom_list
