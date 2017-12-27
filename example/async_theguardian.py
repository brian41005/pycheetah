# coding: utf-8
'''
async version
'''


import os
import re
import sys
import unicodedata

import aiohttp
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


class DailyPage(pycheetah.AsyncCheetah):

    async def request(self, url):
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    soup = BeautifulSoup(await resp.text(), 'lxml')
                    return soup
        except aiohttp.ClientConnectorError:
            return self.retry()

    def get_urls(self, soup):
        urls = []
        for news_block in soup.find_all('div',
                                        attrs={'class': 'fc-item__content'}):
            for each_block in news_block.find_all('a', href=True):
                if each_block['href'] != ''\
                        and each_block['href'] is not None\
                        and each_block['href'].find('https://www.theguardian.com') != -1:
                    urls.append(each_block['href'])
        return urls


def main():
    category = ['world', 'politics', 'sport', 'football', 'culture',
                'business', 'lifeandstyle', 'fashion', 'environment',
                'technology', 'travel']
    all_daily_urls = list(pycheetah.gen_urls('https://www.theguardian.com/%s/%s/all',
                                             '2017/1/1',
                                             '2017/1/1',
                                             product=[category, 'date']))
    pycheetah.init_logger()
    result = pycheetah.start(all_daily_urls, DailyPage)
    # print(result)
    assert result.reduce_by('urls') != []


if __name__ == '__main__':
    main()
