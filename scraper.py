import re
import bs4 as bs
from urllib.parse import urlparse


def scraper(url, resp, saved, report):
    # TODO:
    # 1) check if longest page found so far
    # 2) if subdomain, get unique url count
    # 3) only process page info if is_valid
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link, saved)]


def page_length(url):
    # TODO:
    # 1) strip html
    # 2) get word frequencies skipping stopwords
    # 3) store word frequencies
    # - save as local dict
    # - update global dict
    # 4) return word_count
    # - length of local dict
    pass


def extract_next_links(url, resp):
    # TODO:
    # 1) pull all valid links from page
    print("\n" + url)
    soup = bs.BeautifulSoup(resp.raw_response, 'html.parser')
    links = soup.find_all('a', attrs={'href': '*'})
    return list()


def is_valid(url, saved):
    # TODO: add rules for valid url's
    # 1) url not valid if in saved
    # - defrag before checking if in saved
    # 2) increment a counter for url not in saved
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
