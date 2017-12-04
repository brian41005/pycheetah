# coding: utf-8
import unittest
import sys
import os
from bs4 import BeautifulSoup
import requests
import re
pkg_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(pkg_dir, 'example'))
import pycheetah


class TestUtils(unittest.TestCase):
    def test_partition(self):
        for i in range(1, 11):
            self.assertEqual(
                i, len(list(pycheetah.partition(list(range(10)), i))))

    def test_gen_urls_for_guardian(self):
        Classification = ['world', 'politics', 'sport', 'football', 'culture',
                          'business', 'lifeandstyle', 'fashion', 'environment',
                          'technology', 'travel']

        l = [i for i in pycheetah.gen_urls('https://www.theguardian.com/%s/%s/all',
                                           '2017/1/1',
                                           '2017/1/5',
                                           product=[Classification, 'date'])]
        self.assertEqual(55, len(l))

    def test_gen_urls_for_nyt(self):
        l = [i for i in pycheetah.gen_urls('http://www.nytimes.com/indexes/%s/todayspaper/index.html',
                                           '2017/1/1',
                                           '2017/1/5',
                                           date_format='%Y/%m/%d',
                                           product=['date'])]
        print(l)
        self.assertEqual(5, len(l))

    def test_get_urls_exception(self):
        Classification = ['world']
        with self.assertRaises(ValueError):
            [i for i in pycheetah.gen_urls(
                'https://www.theguardian.com/%s/%s/all',
                '2017/1/0',
                '2017/1/5',
                product=[Classification, 'date'])]
