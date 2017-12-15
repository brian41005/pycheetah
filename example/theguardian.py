# coding: utf-8
# this is a example for The Guardian web


import logging
import os
import pickle
import re
import sys
import time
import unicodedata
import random

import requests
from requests.exceptions import ReadTimeout, ConnectionError
from bs4 import BeautifulSoup


pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pkg_dir)
import pycheetah

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/\
    webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,ms;q=0.6,zh-CN;q\
    =0.5,ja;q=0.4',
    'cache-control': 'no-cache',
    'cookie': 'sbi_debug=false; GU_mvt_id=435928; GU_geo_continent=AS;\
     sbi_debug=false',
    'pragma': 'no-cache',
    'referer': 'https://www.theguardian.com/international',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
    537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}


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


class DailyPage(pycheetah.Cheetah):
    def request(self, url):
        try:
            soup = BeautifulSoup(requests.get(url,
                                              timeout=10,
                                              headers=headers).text,
                                 'lxml')
            return soup
        except (ReadTimeout, ConnectionError):
            logging.info('RETRY [%s][%s]' % (self.name, url.split('/')[-1]))
            return self.retry()

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


class NewsPage(pycheetah.Cheetah):
    def request(self, url):
        try:
            res = requests.get(url, timeout=3, headers=headers)
            if res:
                soup = BeautifulSoup(res.text, 'lxml')
                return soup
        except (ReadTimeout, ConnectionError):
            return self.retry()

    def get_name(self, soup):
        name = soup.find('h1', attrs={'class': 'content__headline',
                                      'itemprop': 'headline'})
        if name:
            return rm_url_tag(str(name)).strip()

    def get_article(self, soup):
        article = ''
        attrs = {'class': 'content__article-body from-content-api js-article__body',
                 'itemprop': 'articleBody',
                 'data-test-id': 'article-review-body'}

        for articleBody in soup.find_all('div', attrs=attrs):
            for each_p in articleBody.find_all('p'):
                article += process(rm_url_tag(each_p.text))

        return article

    def get_category(self, soup):
        return soup.find('link', attrs={'rel': 'canonical'})['href'].split('/')[3]


if __name__ == '__main__':
    Classification = ['world', 'politics', 'sport', 'football', 'culture',
                      'business', 'lifeandstyle', 'fashion', 'environment',
                      'technology', 'travel']
    all_daily_urls = list(pycheetah.gen_urls('https://www.theguardian.com/%s/%s/all',
                                             '2017/1/1',
                                             '2017/1/1',
                                             product=[Classification, 'date']))

    pycheetah.init_logger()

    result = pycheetah.start(all_daily_urls, DailyPage)
    urls = result.reduce_by('urls')
    result = pycheetah.start(urls, NewsPage)
    result.save('theguardian.csv')
