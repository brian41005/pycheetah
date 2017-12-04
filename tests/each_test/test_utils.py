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

    def test_gen_urls(self):
        Classification = ['world']
        l = [i for i in pycheetah.gen_urls('2007/1/1',
                                           '2017/5/31', Classification)]
        self.assertEqual(3804, len(l))

    def test_get_urls_exception(self):
        Classification = ['world']
        with self.assertRaises(ValueError):
            [i for i in pycheetah.gen_urls(
                '2007/1/1',
                '2017/5/32',
                Classification)]
