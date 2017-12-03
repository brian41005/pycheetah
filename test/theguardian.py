# coding: utf-8
# this is a example for The Guardian web

import itertools
import os
import re
import sys
import time
import unicodedata
from multiprocessing import Pool, Process

import requests
from bs4 import BeautifulSoup


pkg_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(pkg_dir)
import pycheetah

Classification = ['world', 'politics', 'sport', 'football', 'culture',
                  'business', 'lifeandstyle', 'fashion', 'environment',
                  'technology', 'travel']
all_urls = [i for i in pycheetah.gen_urls('2010/1/1',
                                          '2017/12/1',
                                          Classification)]

news_list = ['https://www.theguardian.com/business/2014/may/25/astrazeneca-free-pfizer-for-now',
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


class NewsPage(pycheetah.Page):
    def request(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        soup = BeautifulSoup(requests.get(url,
                                          timeout=5,
                                          headers=headers).text,
                             'lxml')
        return soup

    def get_name(soup):
        name = soup.find('h1',
                         attrs={'class': 'content__headline',
                                'itemprop': 'headline'})
        if name:
            return rm_url_tag(str(name)).strip()
        # except (IndexError, AttributeError, UnicodeEncodeError) as errmsg:
        # logging.exception(errmsg, soup.find(
        # 'link', attrs={'rel': 'canonical'})['href'])

    def get_article(soup):
        article = ''
        for articleBody in soup.find_all('div',
                                         attrs={'class': 'content__article-body from-content-api js-article__body',
                                                'itemprop': 'articleBody',
                                                'data-test-id': 'article-review-body'
                                                }):

            for each_p in articleBody.find_all('p'):
                article += process(rm_url_tag(each_p.text))

        return article

    def get_category(soup):
        return soup.find('link', attrs={'rel': 'canonical'})['href'].split('/')[3]


class DailyPage(pycheetah.Page):
    def request(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        soup = BeautifulSoup(requests.get(url,
                                          timeout=5,
                                          headers=headers).text,
                             'lxml')
        return soup

    def get_urls(soup):
        urls = []
        for news_block in soup.find_all('div',
                                        attrs={'class': 'fc-item__content'}):
            for each_block in news_block.find_all('a', href=True):
                if each_block['href'] != '' \
                        and each_block['href'] is not None \
                        and each_block['href'].find('https://www.theguardian.com') != -1:
                    urls.append(each_block['href'])
        return urls


class DailyPageManager(pycheetah.TaskManager):
    __page_class__ = DailyPage


class NewsPageManager(pycheetah.TaskManager):
    __page_class__ = NewsPage


if __name__ == '__main__':

    pycheetah.init_logger()
    ts = time.time()
    result = pycheetah.start(all_urls[-100:], DailyPageManager)
    print(time.time() - ts)

    # all_news_url = []
    # for i in result:
    #     all_news_url.extend(i['urls'])
    # result = pycheetah.start(all_news_url, NewsPageManager)

    # cost_time = time.time() - ts
    # print(cost_time)
    # print(cost_time / len(result))
