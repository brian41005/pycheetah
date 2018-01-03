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


class Board(pycheetah.Cheetah):
    def request(self, url):
        try:
            res = requests.get(url, timeout=3)
            text = res.text
            return BeautifulSoup(text, 'lxml')
        except (ReadTimeout, ConnectionError) as msg:
            raise pycheetah.Retry

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
            raise pycheetah.Retry

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


def main():
    pycheetah.init_logger()
    urls = list(pycheetah.gen_urls('https://www.ptt.cc/bbs/movie/index%d.html',
                                   product=[list(range(6180, 6189))]))

    result = pycheetah.start(urls, Board)
    urls = result.reduce_by('links')
    yield urls
    reseult = pycheetah.start(urls, Article, verbose=True)
    yield reseult.reduce_by('article')


if __name__ == '__main__':
    main()
