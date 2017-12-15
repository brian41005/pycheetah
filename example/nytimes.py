# coding: utf-8
# this is a example for NYT today's paper

import logging
import os
import sys
import time

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


class DailyPage(pycheetah.Cheetah):
    def request(self, url):
        try:
            return BeautifulSoup(requests.get(url, timeout=5,
                                              headers=headers).text,
                                 'lxml')
        except (ReadTimeout, ConnectionError) as msg:
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
        return urls


class NewsPage(pycheetah.Cheetah):

    def request(self, url):
        try:
            res = requests.get(url, timeout=5, headers=headers)
            if res:
                return BeautifulSoup(res.text, 'lxml')
        except (ReadTimeout, ConnectionError):
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
            article += ' ' + each_p.text
        if article:
            return article

    def get_category(self, soup):
        href = soup.find('link', attrs={'rel': 'canonical'})['href']
        return href.split('/')[6]

    def get_url(self, soup):
        return soup.find('link', attrs={'rel': 'canonical'})['href']


if __name__ == '__main__':
    pycheetah.init_logger()
    urls = list(pycheetah.gen_urls('http://www.nytimes.com/indexes/%s/todayspaper/index.html',
                                   '2017/1/1', '2017/1/1',
                                   date_format='%Y/%m/%d',
                                   product=['date']))

    result = pycheetah.start(urls, DailyPage)
    urls = result.reduce_by('urls')
    result = pycheetah.start(urls, NewsPage)
    result.save('nytimes.csv')
