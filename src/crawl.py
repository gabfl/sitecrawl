import argparse

import requests
from bs4 import BeautifulSoup

valid_content_types = [
    'text/html',
]
crawling_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "accept-language": "en-US,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "DNT": "1",
    "Pragma": "no-cache",
    "Referer": "http://www.google.com",
}
crawling_timeout = 3
base_url = None
no_pound = False
no_get = False
no_validate_ct = False
verbose = False
max_crawl = 0
scanned_urls = []
internal_urls = []
skipped_urls = []
external_urls = []
requests_cache = {}


def is_same_website(base, url):
    """ Checks if the URL is on the same website """

    if url.startswith('http'):
        return url.startswith(base)
    else:
        return True


def relative_to_absolute(base, url):
    """ Transforms a relative URL in an absolute URL """

    if url.startswith('http'):
        return url
    elif url.startswith('/'):
        return base + url
    else:
        return base + '/' + url


def discard_after_character(url, character='#'):
    """ Discard a URL after a character """

    return url.split(character)[0]


def deep_crawl(depth=2):
    """ Scan a list of URLs """

    global internal_urls

    # Load initial URL
    request_res = load_url(base_url)
    if not request_res:
        return False

    # Add the first URL to the list of scanned URLs
    internal_urls = [request_res.url]

    # Loop repeatedly through URLs to achieve desired depth
    for x in range(depth):
        if verbose:
            print('* Depth: ' + str(x + 1))
        for url in internal_urls:
            # print(url)
            if url not in scanned_urls:
                scan_url(url)

                # Limit crawl
                if max_crawl > 0 and len(internal_urls) >= max_crawl:
                    return


def scan_url(url):
    """ Scan a URL """

    if verbose:
        print('* Scanning: ' + url)

    # Add to list of scanned URLs
    scanned_urls.append(url)

    # Load page
    request_res = load_url_from_cache(url) or load_url(url)
    if not request_res:
        return False

    # Parse HTML
    soup = parse_html(request_res)

    # Find URLs within the page
    find_urls(soup)

    return True


def load_url(url, validate_result=True):
    """ Loads a page and returns the request response """

    try:
        r = requests.get(
            url,
            allow_redirects=True,
            headers=crawling_headers,
            timeout=crawling_timeout
        )
    except requests.exceptions.ReadTimeout as e:
        if verbose:
            print('! Error: ' + str(e))
        return False

    if validate_result:
        # Discard non 2xx/3xx responses
        if not is_valid_status_code(r):
            if verbose:
                print('! Error: status code ' + str(r.status_code))
            return False

        # Validate content type
        if not is_valid_content_type(r):
            if verbose:
                print('! Error: Invalid content type')
            return False

    # Add to cache
    requests_cache[url] = r  # Cache requested URL
    if url != r.url:
        requests_cache[r.url] = r  # Cache actual URL

    return r


def load_url_from_cache(url):
    """ Returns the request response from the cache """

    if url in requests_cache:
        # print('* Cached: ' + url)
        return requests_cache[url]

    return None


def is_valid_status_code(request):
    """ Checks if the status code is valid """

    return request.status_code >= 200 and request.status_code < 400


def is_valid_content_type(request):
    """ Checks if the content type is valid """

    if no_validate_ct:
        return True

    for valid_content_type in valid_content_types:
        if request.headers.get('content-type') and valid_content_type in request.headers['content-type'].lower():
            return True

    return False


def parse_html(request_res):
    """ Parses the HTML of a page """

    soup = BeautifulSoup(request_res.text, 'html.parser')
    return soup


def get_internal_urls():
    """ Returns the list of internal URLs """

    return internal_urls


def get_external_urls():
    """ Returns the list of external URLs """

    return external_urls


def get_skipped_urls():
    """ Returns the list of skipped URLs """

    return skipped_urls


def find_urls(soup):
    """ Finds all the URLs in a page """

    global internal_urls, skipped_urls, external_urls

    for link in soup.find_all('a'):
        url = link.get('href')
        if url:
            # Remove spaces
            url = url.strip()

            if is_same_website(base_url, url):
                url = relative_to_absolute(base_url, url)

                if no_pound:
                    url = discard_after_character(url)

                if no_get:
                    url = discard_after_character(url, '?')

                # Load page
                r = load_url_from_cache(url) or load_url(url, False)
                if not r:
                    if verbose:
                        print('! Skipping: Invalid page response')
                    continue

                # Set page URL (which may have been modified by a redirect)
                page_url = r.url

                if page_url not in internal_urls and page_url not in skipped_urls:
                    if verbose:
                        print('* Found internal URL:', url)

                    # Validate status code
                    if not is_valid_status_code(r):
                        skipped_urls = skipped_urls + [page_url]
                        if verbose:
                            print('! Skipping: status code',
                                  str(r.status_code))
                        continue

                    # Validate content type
                    if not is_valid_content_type(r):
                        skipped_urls = skipped_urls + [page_url]
                        if verbose:
                            print('! Skipping: Invalid content type')
                        continue

                    internal_urls = internal_urls + [page_url]

                    # Limit crawl
                    if max_crawl > 0 and len(internal_urls) >= max_crawl:
                        return
            else:  # Different website
                if url not in external_urls:
                    external_urls = external_urls + [url]
                    if verbose:
                        print('* Found external URL:', url)


def main():
    global base_url, no_pound, no_get, no_validate_ct, verbose, max_crawl

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", type=str,
                        help="URL to crawl", required=True)
    parser.add_argument("-d", "--depth", type=int,
                        help="Depth of the crawl", default=1)
    parser.add_argument("-p", "--no_pound",
                        action='store_true', help="Discard local anchors")
    parser.add_argument("-g", "--no_get", action='store_true',
                        help="Discard GET parameters")
    parser.add_argument("-c", "--no_validate_ct", action='store_true',
                        help="Accept non text/html content types")
    parser.add_argument("-m", "--max", type=int,
                        help="Max number of internal URLs to return (allows to limit crawling of a large website)", default=0)
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="Verbose mode")
    args = parser.parse_args()

    # Set variables
    base_url = args.url
    no_pound = args.no_pound
    no_get = args.no_get
    no_validate_ct = args.no_validate_ct
    verbose = args.verbose
    max_crawl = args.max

    deep_crawl(args.depth)

    # Print results
    print('* Found ' + str(len(get_internal_urls())) + ' internal URLs')
    for url in get_internal_urls():
        print('  ' + url)

    print()
    print('* Found ' + str(len(get_external_urls())) + ' external URLs')
    for url in get_external_urls():
        print('  ' + url)

    print()
    print('* Skipped ' + str(len(get_skipped_urls())) + ' URLs')
    for url in get_skipped_urls():
        print('  ' + url)


if __name__ == '__main__':
    main()
