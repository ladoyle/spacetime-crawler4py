import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def scraper(url, resp, saved, report):
    # only process OK responses
    if resp.status == 200:
        length = page_length(resp, report)
        if length > report.get_longest():
            report.update_longest(length)
        elif length == 0:
            return list()
        # pull all valid links in page
        links = extract_next_links(url, resp, saved, report)
        return [link for link in links]
    else:
        return list()


def page_length(resp, report):
    # TODO:
    # 1) check page similarity by stats analysis

    # get only the text from the html response
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    data = soup.get_text()
    # extract word tokens skipping stopwords
    words = tokenize(data)
    # store word frequencies
    frequency_map = compute_word_frequency(words)
    report.update_common(frequency_map)
    # return word count as page_length
    return len(frequency_map)


def tokenize(data):
    # create a set of stopwords from file
    stopwords = set()
    with open('stopwords.txt') as stopwords_file:
        while True:
            word = stopwords_file.readline()
            if not word:
                break
            stopwords.add(word.strip())
    # create a list of tokenized words from page content
    page_words = []
    for word in re.split(r'\W+', data):
        if word.isalnum() and len(word) > 1:
            page_words.append(word.lower())
    # return a list of words that are in page_words but not the stopwords
    return [word for word in page_words if word not in stopwords]


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
    links = soup.find_all('a')
    valid_links = []
    for link in links:
        if is_valid(link.get('href'), saved):
            # create a list of only valid links
            valid_links.append(link)
    # check if this url is a sub-domain of ics.uci.edu
    check_sub_domain(url, report, len(valid_links))
    return valid_links


def check_sub_domain(url, report, num_links):
    # TODO:
    # 1) check if url is a sub-domain of ics.uci.edu
    # 2) if yes add to the report with num_links
    pass


def is_valid(url, saved):
    # TODO: add rules for valid url's
    # 1) url not valid if in saved
    # - defrag before checking if in saved
    # 2) update unique url count in report
    # 3) not valid if not a in the seed domains
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
    except TypeError:
        print("TypeError for ", parsed)
        raise
