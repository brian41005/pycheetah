# coding: utf-8
# this is a example for The Guardian web

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


def rm_url_tag(seq, pattern='<.*?>'):
    return re.sub(re.compile(pattern), '', seq)


def process(article):
    article = unicodedata.normalize("NFKD", article)
    article = article.encode(
        'utf-8', 'ignore').decode("utf-8", "ignore")
    article = article.strip(' ').strip('\n').strip('\r\n')
    article = re.sub('[^a-zA-Z]', ' ', article)
    article = re.sub(' . ', ' ', article)
    return article


class DailyPage(pycheetah.Page):
    def request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        soup = BeautifulSoup(requests.get(url,
                                          timeout=10,
                                          headers=headers).text,
                             'lxml')
        return soup

    def get_urls(self, soup):
        urls = []
        for news_block in soup.find_all('div',
                                        attrs={'class': 'fc-item__content'}):
            for each_block in news_block.find_all('a', href=True):
                if each_block['href'] != '' \
                        and each_block['href'] is not None \
                        and each_block['href'].find('https://www.theguardian.com') != -1:
                    urls.append(each_block['href'])
        return urls


class NewsPage(pycheetah.Page):
    def request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        soup = BeautifulSoup(requests.get(url,
                                          timeout=10,
                                          headers=headers).text,
                             'lxml')
        return soup

    def get_name(self, soup):
        name = soup.find('h1',
                         attrs={'class': 'content__headline',
                                'itemprop': 'headline'})
        if name:
            return rm_url_tag(str(name)).strip()
        # except (IndexError, AttributeError, UnicodeEncodeError) as errmsg:
        # logging.exception(errmsg, soup.find(
        # 'link', attrs={'rel': 'canonical'})['href'])

    def get_article(self, soup):
        article = ''
        for articleBody in soup.find_all('div',
                                         attrs={'class': 'content__article-body from-content-api js-article__body',
                                                'itemprop': 'articleBody',
                                                'data-test-id': 'article-review-body'
                                                }):

            for each_p in articleBody.find_all('p'):
                article += process(rm_url_tag(each_p.text))

        return article

    def get_category(self, soup):
        return soup.find('link', attrs={'rel': 'canonical'})['href'].split('/')[3]


class DailyPageManager(pycheetah.DefaultTaskManager):
    __page_class__ = DailyPage


class NewsPageManager(pycheetah.DefaultTaskManager):
    __page_class__ = NewsPage


if __name__ == '__main__':
    pycheetah.CORE = 1
    pycheetah.NUM_THREAD = 1
    Classification = ['world', 'politics', 'sport', 'football', 'culture',
                      'business', 'lifeandstyle', 'fashion', 'environment',
                      'technology', 'travel']
    all_daily_urls = list(pycheetah.gen_urls('https://www.theguardian.com/%s/%s/all',
                                             '2017/1/1',
                                             '2017/1/2',
                                             product=[Classification, 'date']))

    pycheetah.init_logger()
    ts = time.time()
    result = pycheetah.start(all_daily_urls, DailyPageManager)

    all_news_urls = []
    for i in result:
        if i['urls'] is not None:
            all_news_urls.extend(i['urls'])
    result = pycheetah.start(all_news_urls, NewsPageManager)

    cost_time = time.time() - ts
    print('time:%.6f, %d data, avg:%.6f' %
          (cost_time, len(result), cost_time / len(result)))
