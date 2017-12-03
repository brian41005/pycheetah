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
        self.news_list = ['https://www.theguardian.com/business/2014/may/25/astrazeneca-free-pfizer-for-now',
                          'https://www.theguardian.com/world/2010/feb/23/nicaragua-cancer-treatment-abortion',
                          'https://www.theguardian.com/business/2010/feb/23/protesters-blockade-greek-stock-exchange',
                          'https://www.theguardian.com/world/2010/feb/23/us-army-chief-end-anti-gay-rules',
                          'https://www.theguardian.com/world/2010/feb/23/china-denies-google-cyber-attacks',
                          'https://www.theguardian.com/world/2010/feb/23/bomb-maker-stay-in-service-iraq',
                          'https://www.theguardian.com/world/2010/feb/23/dennis-brutus-obituary',
                          'https://www.theguardian.com/world/2010/feb/23/corrie-death-law-case',
                          'https://www.theguardian.com/world/2010/feb/23/kenya-president-prime-minister-meet',
                          'https://www.theguardian.com/world/2010/feb/23/british-woman-killed-swat-valley',
                          'https://www.theguardian.com/world/2010/feb/23/china-tells-schools-ban-oxfam',
                          'https://www.theguardian.com/world/2010/feb/23/indonesia-ranger-komodo-dragon-attack',
                          'https://www.theguardian.com/world/2010/feb/23/british-plane-spotters-face-jail-india',
                          'https://www.theguardian.com/world/2010/feb/23/32-missing-madeira-landslides-search',
                          'https://www.theguardian.com/world/julian-borger-global-security-blog/2010/feb/23/iran-iaea-letter',
                          'https://www.theguardian.com/world/2010/feb/23/taliban-captured-pakistan-abdul-kabir',
                          'https://www.theguardian.com/world/blog/audio/2010/feb/22/guardian-daily-podcast1',
                          'https://www.theguardian.com/world/picture/2010/feb/23/usa-air-transport']

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
    unittest.main(verbosity=2)
    pass
