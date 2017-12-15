# coding: utf-8
# this is a example for NYT today's paper

import logging
import os
import sys
import time

import requests
from bs4 import BeautifulSoup


pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pkg_dir)
import pycheetah


class DailyPage(pycheetah.Cheetah):
    def request(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            return BeautifulSoup(requests.get(url, timeout=3,
                                              headers=headers).text,
                                 'lxml')
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError) as msg:
            return self.retry()

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

        # logging.info('[%s]' % (len(urls)))
        return urls


class NewsPage(pycheetah.Cheetah):

    def request(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            t0 = time.time()
            res = requests.get(url, timeout=3, headers=headers)
            if res:
                soup = BeautifulSoup(res.text, 'lxml')
                #logging.info('[%s][%s]' % (self.name, url.split('/')[-1]))
                return soup

        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError):
            logging.info('RETRY [%s][%s]' % (self.name, url.split('/')[-1]))
            return self.retry()

    def get_title(self, soup):
        name = soup.find('h6', attrs={'class': 'kicker'})
        if name:
            name = name.text
        else:
            name = soup.find(
                'span', attrs={'class': 'Heading1-headline--8Qzcc balance-text'})
            if name:
                name = name.text

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


if __name__ == '__main__':
    pycheetah.init_logger()
    t0 = time.time()

    urls = list(pycheetah.gen_urls('http://www.nytimes.com/indexes/%s/todayspaper/index.html',
                                   '2017/1/1', '2017/1/20',
                                   date_format='%Y/%m/%d',
                                   product=['date']))

    result = pycheetah.start(urls, DailyPage)
    urls = result.reduce_key('urls')
    result = pycheetah.start(urls, NewsPage)
    t1 = time.time() - t0
    print('time:%.6f, %d data, avg:%.6f' % (t1, len(result),
                                            t1 / len(result)))
    print(len(urls))
