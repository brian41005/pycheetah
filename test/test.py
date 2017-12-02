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
        try:
            name = soup.findAll('h1',
                                attrs={'class': 'content__headline',
                                       'itemprop': 'headline'})[0]
            return rm_url_tag(str(name)).strip()
        except (IndexError, AttributeError, UnicodeEncodeError) as errmsg:
            print(errmsg)

    def get_article(soup):
        article = ''
        for articleBody in soup.findAll('div',
                                        attrs={'class': 'content__article-body from-content-api js-article__body',
                                               'itemprop': 'articleBody',
                                               'data-test-id': 'article-review-body'
                                               }):

            for each_p in articleBody.findAll('p'):
                article += process(rm_url_tag(each_p.text))

        return article

    def get_category(soup):
        return soup.find('link', attrs={'rel': 'canonical'})['href'].split('/')[3]


class TestPage(unittest.TestCase):
    def setUp(self):
        import urls
        self.urls_list = urls.urlList

    def test_Page(self):

        pages = [MyPageWorker(str(i), url)
                 for i, url in enumerate(self.urls_list)]
        for page in pages:
            page.start()
        for page in pages:
            result = page.join()
            for k, v in result.items():
                try:
                    self.assertIsNotNone(v, (page.url, {k: v}))
                except AssertionError:
                    pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
