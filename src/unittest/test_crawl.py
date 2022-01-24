import unittest

import requests
from bs4 import BeautifulSoup

from .. import crawl


class Test(unittest.TestCase):

    def setUp(self):
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

    def test_truncate_last_slash(self):
        assert crawl.truncate_last_slash(
            'http://www.gab.lc/') == 'http://www.gab.lc'
        assert crawl.truncate_last_slash(
            'http://www.gab.lc') == 'http://www.gab.lc'

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

    def test_scan_url(self):
        crawl.base_url = 'https://github.com'
        res = crawl.scan_url('https://github.com')

        assert res is True

        # Test invalid URL
        res = crawl.scan_url('https://www.gab.lc/some_404_page')
        assert res is False

    def test_load_headers(self):
        assert isinstance(crawl.load_headers(
            'https://github.com'), requests.models.Response)

    def test_is_valid_status_code(self):
        r = crawl.load_headers('https://www.gab.lc')
        assert crawl.is_valid_status_code(r) is True

        r = crawl.load_headers('https://www.gab.lc/some_404_page')
        assert crawl.is_valid_status_code(r) is False

    def test_is_valid_content_type(self):
        r = crawl.load_headers('https://www.gab.lc')
        assert crawl.is_valid_content_type(r) is True

        # Invalid headers
        r = crawl.load_headers(
            'https://www.gab.lc/static/misc/gpg.txt')
        assert crawl.is_valid_content_type(r) is False

        # Test invalid content type with override flag
        crawl.no_validate_ct = True
        assert crawl.is_valid_content_type(r) is True
        crawl.no_validate_ct = False  # Restore default

    def test_load_page(self):
        assert isinstance(crawl.load_page(
            'https://github.com/'), BeautifulSoup)

        # Test 404 page
        assert crawl.load_page('http://www.gab.lc/some_404_page') is False

        # Test page with invalid content type
        assert crawl.load_page(
            'https://www.gab.lc/static/misc/gpg.txt') is False

    def test_find_urls(self):
        crawl.no_pound = True
        crawl.no_get = True

        crawl.base_url = 'https://www.gab.lc'
        soup = crawl.load_page('https://www.gab.lc')
        res = crawl.find_urls(soup)
        assert res is None

        # Test with invalid status code
        crawl.base_url = 'https://httpstat.us'
        soup = crawl.load_page('https://httpstat.us')
        res = crawl.find_urls(soup)
        assert res is None
