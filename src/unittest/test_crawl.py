import unittest

import requests
from bs4 import BeautifulSoup

from .. import crawl


class Test(unittest.TestCase):

    def setUp(self):
        crawl.max_crawl = 5
        crawl.verbose = True

    def test_is_same_website(self):
        assert crawl.is_same_website(
            'http://www.gab.lc/', 'http://www.gab.lc/something') is True
        assert crawl.is_same_website(
            'http://www.gab.lc/', '/something/') is True
        assert crawl.is_same_website(
            'http://www.gab.lc/', 'something/') is True
        assert crawl.is_same_website(
            'http://www.gab.lc/', 'https://github.com/') is False

    def test_relative_to_absolute(self):
        assert crawl.relative_to_absolute(
            'http://www.gab.lc', 'http://www.gab.lc') == 'http://www.gab.lc'
        assert crawl.relative_to_absolute(
            'http://www.gab.lc', '/something') == 'http://www.gab.lc/something'
        assert crawl.relative_to_absolute(
            'http://www.gab.lc', 'something') == 'http://www.gab.lc/something'

    def test_discard_after_character(self):
        assert crawl.discard_after_character(
            'http://www.gab.lc/') == 'http://www.gab.lc/'
        assert crawl.discard_after_character(
            'http://www.gab.lc/?foo=bar', '?') == 'http://www.gab.lc/'
        assert crawl.discard_after_character(
            'http://www.gab.lc/#foobar') == 'http://www.gab.lc/'

    def test_deep_crawl(self):
        crawl.base_url = 'https://www.gab.lc'
        crawled = crawl.deep_crawl(1)
        assert crawled is None

        assert isinstance(crawl.get_internal_urls(), list)
        assert isinstance(crawl.get_external_urls(), list)
        assert isinstance(crawl.get_skipped_urls(), list)

        # Test invalid URL
        crawl.base_url = 'https://www.gab.lc/some_404_page'
        assert crawl.deep_crawl(1) is False

    def test_scan_url(self):
        crawl.base_url = 'https://github.com'
        res = crawl.scan_url('https://github.com')
        assert res is True

        # Test invalid URL
        res = crawl.scan_url('https://www.gab.lc/some_404_page')
        assert res is False

    def test_load_url(self):
        url = 'https://github.com/'
        res = crawl.load_url(url)
        assert isinstance(res, requests.models.Response)

        # Test cache (requested URL)
        assert url in crawl.requests_cache
        assert isinstance(
            crawl.requests_cache[url], requests.models.Response)

        # Test cache (actual URL)
        assert res.url in crawl.requests_cache
        assert isinstance(
            crawl.requests_cache[res.url], requests.models.Response)

        # Test 404 page
        res = crawl.load_url(
            'http://www.gab.lc/some_404_page')
        assert res is False

        # Test page with invalid content type
        res = crawl.load_url(
            'https://www.gab.lc/static/misc/gpg.txt')
        assert res is False

    def test_load_url_from_cache(self):

        # Test unknown URL
        res = crawl.load_url_from_cache('http://www.somenewurl.com')
        assert res is None

        # Test known URL
        url = 'https://github.com'
        crawl.load_url(url)
        res = crawl.load_url_from_cache(url)
        assert isinstance(res, requests.models.Response)

    def test_is_valid_status_code(self):
        r = crawl.load_url('https://www.gab.lc', validate_result=False)
        assert crawl.is_valid_status_code(r) is True

        r = crawl.load_url('https://www.gab.lc/some_404_page',
                           validate_result=False)
        assert crawl.is_valid_status_code(r) is False

    def test_is_valid_content_type(self):
        r = crawl.load_url('https://www.gab.lc', validate_result=False)
        assert crawl.is_valid_content_type(r) is True

        # Invalid headers
        r = crawl.load_url(
            'https://www.gab.lc/static/misc/gpg.txt', validate_result=False)
        assert crawl.is_valid_content_type(r) is False

        # Test invalid content type with override flag
        crawl.no_validate_ct = True
        assert crawl.is_valid_content_type(r) is True
        crawl.no_validate_ct = False  # Restore default

    def parse_html(self):
        request_res = crawl.load_url('https://github.com/')
        soup = crawl.parse_html(request_res)
        assert isinstance(soup, BeautifulSoup)

    def test_find_urls(self):
        crawl.no_pound = True
        crawl.no_get = True

        crawl.base_url = 'https://www.gab.lc'
        request_res = crawl.load_url('https://www.gab.lc')
        soup = crawl.parse_html(request_res)
        assert crawl.find_urls(soup) is None

        # Test with invalid status code
        crawl.base_url = 'https://httpstat.us'
        request_res = crawl.load_url('https://httpstat.us')
        soup = crawl.parse_html(request_res)
        assert crawl.find_urls(soup) is None
