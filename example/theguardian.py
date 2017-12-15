# coding: utf-8
# this is a example for The Guardian web


import os
import re
import sys
import time
import logging
import unicodedata
import requests
from bs4 import BeautifulSoup
import pickle

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


class DailyPage(pycheetah.Cheetah):
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


class NewsPage(pycheetah.Cheetah):
    def request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        try:
            res = requests.get(url,
                               timeout=10,
                               headers=headers)
            if res:
                soup = BeautifulSoup(res.text,
                                     'lxml')
                # logging.info('[%s][%s]' % (self.name, url.split('/')[-1]))
                return soup

        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError):
            logging.info('RETRY [%s][%s]' % (self.name, url.split('/')[-1]))
            return self.retry()

    def get_name(self, soup):
        name = soup.find('h1',
                         attrs={'class': 'content__headline',
                                'itemprop': 'headline'})
        if name:
            return rm_url_tag(str(name)).strip()

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


if __name__ == '__main__':
    Classification = ['world', 'politics', 'sport', 'football', 'culture',
                      'business', 'lifeandstyle', 'fashion', 'environment',
                      'technology', 'travel']
    all_daily_urls = list(pycheetah.gen_urls('https://www.theguardian.com/%s/%s/all',
                                             '2017/1/1',
                                             '2017/1/1',
                                             product=[Classification, 'date']))

    pycheetah.init_logger()
    ts = time.time()

    result = pycheetah.start(all_daily_urls, DailyPage)
    urls = result.reduce_key('urls')
    result = pycheetah.start(urls, NewsPage)

    cost_time = time.time() - ts
    print('time:%.6f, %d data, avg:%.6f' %
          (cost_time, len(result), cost_time / len(result)))
    print(len(urls))
    with open('result.pkl', 'wb') as f:
        pickle.dump(result, f)
    result.save('theguardian.csv')
