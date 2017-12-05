# coding: utf-8
# this is a example for NYT today's paper

import itertools
import os
import re
import sys
import time
import unicodedata

import requests
from bs4 import BeautifulSoup


pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pkg_dir)
import pycheetah

all_daily_urls = list(pycheetah.gen_urls('http://www.nytimes.com/indexes/%s/todayspaper/index.html',
                                         '2017/1/1', '2017/12/1',
                                         date_format='%Y/%m/%d',
                                         product=['date']))


class DailyPage(pycheetah.Page):
    def request(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        return BeautifulSoup(requests.get(url, timeout=5,
                                          headers=headers).text,
                             'lxml')

    def get_urls(soup):
        urls = []
        acolumn_a = soup.find_all('div',
                                  attrs={'class': 'columnGroup first'})[2].find_all('a')
        for i in acolumn_a:
            urls.append(i['href'])

        for each_ul in soup.find_all('ul',
                                     attrs={'class': 'headlinesOnly multiline flush'})[:-1]:
            for i in each_ul.find_all('a'):
                urls.append(i['href'])

        return urls


class DailyPageManager(pycheetah.TaskManager):
    __page_class__ = DailyPage


if __name__ == '__main__':

    pycheetah.init_logger()
    ts = time.time()
    result = pycheetah.start(all_daily_urls, DailyPageManager)
    cost_time = time.time() - ts
    print('time:%.6f, %d data, avg:%.6f' %
          (cost_time, len(result), cost_time / len(result)))
