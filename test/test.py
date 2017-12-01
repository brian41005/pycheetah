# coding: utf-8
import os
import re
import sys
import unicodedata
import unittest

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


class MyPageWorker(pycheetah.Page):
    def request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        soup = BeautifulSoup(requests.get(url,
                                          timeout=5,
                                          headers=headers).text,
                             'lxml')
        return soup

    def get_name(self, soup):
        try:
            name = soup.findAll('h1',
                                attrs={'class': 'content__headline',
                                       'itemprop': 'headline'})[0]
            return rm_url_tag(str(name)).strip()
        except (IndexError, AttributeError, UnicodeEncodeError) as errmsg:
            print(errmsg)

    def get_article(self, soup):
        article = ''
        for articleBody in soup.findAll('div',
                                        attrs={'class': 'content__article-body from-content-api js-article__body',
                                               'itemprop': 'articleBody',
                                               'data-test-id': 'article-review-body'
                                               }):

            for each_p in articleBody.findAll('p'):
                each_p = process(rm_url_tag(each_p.text))
                if each_p != '':
                    article += each_p

        return article


if __name__ == '__main__':
    mypage_worker = MyPageWorker(
        'QQ', 'https://www.theguardian.com/business/2014/may/25/astrazeneca-free-pfizer-for-now')
    mypage_worker.start()
    print(mypage_worker.join())
