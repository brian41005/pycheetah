# coding:utf-8
import logging
import os
import re
import sys
import time
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, ReadTimeout

pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pkg_dir)
import pycheetah


# headers = {
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/\
# webp,image/apng,*/*;q=0.8',
#     'accept-encoding': 'gzip, deflate, br',
#     'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,ms;q=0.6,zh-CN;q\
# =0.5,ja;q=0.4',
#     'cache-control': 'no-cache',
#     'cookie': 'sbi_debug=false; GU_mvt_id=435928; GU_geo_continent=AS;\
# sbi_debug=false',
#     'pragma': 'no-cache',
#     'referer': 'https://www.theguardian.com/international',
#     'upgrade-insecure-requests': '1',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
# 537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}


class Board(pycheetah.Cheetah):
    def request(self, url):
        try:
            res = requests.get(url, timeout=3)
            text = res.text
            return BeautifulSoup(text, 'lxml')
        except (ReadTimeout, ConnectionError) as msg:
            return self.retry()

    def get_links(self, soup):
        soup = soup.find('div',
                         attrs={'class': 'r-list-container action-bar-margin bbs-screen'})
        links = [urljoin('https://www.ptt.cc', each_a['href'])
                 for each_a in soup.find_all('a')]
        return links


class Article(pycheetah.Cheetah):
    def request(self, url):
        try:
            res = requests.get(url, timeout=3)
            text = res.text
            return BeautifulSoup(text, 'lxml')
        except (ReadTimeout, ConnectionError) as msg:
            return self.retry()

    def get_title(self, soup):
        title = soup.find_all('span', attrs={'class': 'article-meta-value'})[2]
        return title.text

    def get_article(self, soup):
        article = soup.find(
            'div', attrs={'id': 'main-content',
                          'class': 'bbs-screen bbs-content'})
        text = ' '.join(
            [each for each in article.find_all(text=True, recursive=False)])
        return text.replace('\n', ' ')


if __name__ == '__main__':
    pycheetah.init_logger()
    urls = list(pycheetah.gen_urls('https://www.ptt.cc/bbs/movie/index%d.html',
                                   product=[list(range(5188, 6189))]))

    result = pycheetah.start(urls, Board)
    urls = result.reduce_by('links')
    reseult = pycheetah.start(urls, Article, verbose=True)
    reseult.save('ptt_movie.csv')
