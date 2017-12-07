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


class DailyPage(pycheetah.Cheetah):
    def request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        return BeautifulSoup(requests.get(url, timeout=5,
                                          headers=headers).text,
                             'lxml')

    def get_urls(self, soup):
        urls = []
        acolumn_a = soup.find_all('div',
                                  attrs={'class': 'columnGroup first'})
        if len(acolumn_a) > 1:
            for i in acolumn_a[2].find_all('a'):
                urls.append(i['href'])

        for each_ul in soup.find_all('ul',
                                     attrs={'class': 'headlinesOnly multiline flush'})[:-1]:
            if each_ul:
                for i in each_ul.find_all('a'):
                    urls.append(i['href'])

        return urls


class NewsPage(pycheetah.Cheetah):

    def request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        soup = BeautifulSoup(requests.get(url,
                                          headers=headers).text,
                             'lxml')
        return soup

    def get_title(self, soup):
        name = soup.find('h6', attrs={'class': 'kicker'})
        if name:
            name = name.text
        else:
            name = soup.find(
                'span', attrs={'class': 'Heading1-headline--8Qzcc balance-text'}).text

        return name

    def get_article(self, soup):
        p = soup.find_all(
            'p', attrs={'class': 'story-body-text story-content'})
        article = ''
        for each_p in p:
            article += each_p.text
        if article:
            return article

    def get_category(self, soup):
        return soup.find('link', attrs={'rel': 'canonical'})['href'].split('/')[6]

    def get_url(self, soup):
        return soup.find('link', attrs={'rel': 'canonical'})['href']


# class DailyPageManager(pycheetah.DefaultTaskManager):
#     __page_class__ = DailyPage


# class NewsPageManager(pycheetah.DefaultTaskManager):
#     __page_class__ = NewsPage


if __name__ == '__main__':
    pycheetah.init_logger()
    ts = time.time()

    urls = list(pycheetah.gen_urls('http://www.nytimes.com/indexes/%s/todayspaper/index.html',
                                   '2017/1/1', '2017/12/1',
                                   date_format='%Y/%m/%d',
                                   product=['date']))
    result = pycheetah.start(urls, DailyPage)
    # result = pycheetah.start(result['urls'], NewsPageManager)

    cost_time = time.time() - ts
    print('time:%.6f, %d data, avg:%.6f' %
          (cost_time, len(result),
           cost_time / len(result)))
