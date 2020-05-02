import re
import sys

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from utils import get_urlhash


def scraper(url, resp, saved, report):
    links = []
    # only process OK responses
    if resp.status in {200, 201, 202, 302} and resp.raw_response:
        length = page_length(resp, report)
        # if no data, return empty
        if length == 0:
            return links
        elif length > report.longest_page[1]:
            report.update_longest((url, length))
        # pull all valid links in page
        return extract_next_links(url, resp, saved, report)
    else:
        return links


def page_length(resp, report):
    # get only the text from the html response
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    data = soup.get_text()
    # extract word tokens skipping stopwords
    words = tokenize(data)
    # store word frequencies
    frequency_map = compute_word_frequency(words)
    if len(frequency_map) < 25:
        # don't scrape url's -> low content
        return 0
    # check page similarity with simhash
    hasher = report.simhash
    fingerprint = hasher.create_fingerprint(frequency_map)
    similarity = hasher.calculate_similarity(fingerprint)
    if similarity < 0.10:
        # don't scrape url's -> near duplicate
        return 0
    else:
        report.update_common(frequency_map)
        hasher.save_fingerprint(fingerprint)
        # return word count as page_length
        return len(frequency_map)


def tokenize(data):
    # create a set of stopwords from file
    stopwords = set()
    try:
        with open('stopwords.txt') as stopwords_file:
            while True:
                line = stopwords_file.readline()
                if not line:
                    break
                stopwords.add(line.strip())
        # create a list of tokenized words from page content
        page_words = []
        for word in re.split(r'\W+', data):
            if type(word) is bytes:
                word = word.encode('utf-8')
            if word.isalnum() and len(word) > 1:
                page_words.append(word.lower())
        # return a list of words that are in page_words but not the stopwords
        return [word for word in page_words if word not in stopwords]
    except FileNotFoundError:
        print('Error opening stopwords.txt!!', file=sys.stderr)
        return list()


def compute_word_frequency(words):
    # create a new dictionary with words and frequencies for each word in the list
    frequency_map = dict()
    for word in words:
        if frequency_map.get(word):
            frequency_map[word] += 1
        else:
            frequency_map[word] = 1
    return frequency_map


def extract_next_links(url, resp, saved, report):
    # use beautifulSoup to parse the html content
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    # extract all a tags
    tags = soup.find_all('a')
    valid_links = []
    for tag in tags:
        link = tag.get('href')
        if is_valid(link, saved):
            # create a list of only valid links
            valid_links.append(defrag(link))
    # update the number of unique pages
    report.update_unique(len(valid_links))
    # check if this url is a sub-domain of ics.uci.edu
    check_sub_domain(url, report, len(valid_links))
    return valid_links


def defrag(link):
    parsed = urlparse(link)
    return f'{parsed.scheme}://{parsed.netloc}/{parsed.path}'


def check_sub_domain(url, report, num_links):
    parsed = urlparse(url)
    if re.match(r".+\.ics\.uci\.edu", parsed.netloc) and "www.ics.uci.edu" != parsed.netloc:
        report.update_domains({url: num_links})


def is_valid(url, saved):
    try:
        url = defrag(url)
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        elif saved.get(get_urlhash(url)):
            return False
        elif not re.match(
                r".*(\.ics"
                + r"|\.cs"
                + r"|\.informatics"
                + r"|\.stat"
                + r"|today)"
                  r"\.uci\.edu", parsed.netloc):
            return False
        elif re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|ppsx|diff|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        else:
            if re.match(r"today\.uci\.edu", parsed.netloc) and not re.match(r"//department"
                                                                            r"/information_computer_sciences/*",
                                                                            parsed.path):
                return False
            return True
    except TypeError:
        print("TypeError for ", url)
        raise
