# coding: utf-8
import os
import re
import sys
import time
import unicodedata
import unittest
from collections import deque
from multiprocessing import Process, Pool

import requests
from bs4 import BeautifulSoup

import theguardian


class TestPage(unittest.TestCase):
    def setUp(self):
        self.news_list = theguardian.news_list

    # def test_Page(self):

    #     pages = [theguardian.NewsPage(str(i), url)
    #              for i, url in enumerate(self.news_list)]
    #     for page in pages:
    #         page.start()
    #     for page in pages:
    #         result = page.join()
    #         for k, v in result.items():
    #             try:
    #                 self.assertIsNotNone(v, (page.url, {k: v}))
    #             except AssertionError as msg:
    #                 print(msg)

    def test_TaskManager(self):
        num_thread = 20
        batch = 50
        urls_list = theguardian.all_urls[-batch:]
        print(len(urls_list))
        ts = time.time()
        manager = theguardian.DailyPageManager(urls_list, num_thread)
        manager.start()
        # print(manager.result)
        print((time.time() - ts))
        print((time.time() - ts) / batch)


if __name__ == '__main__':
    # unittest.main(verbosity=2)
    pass
