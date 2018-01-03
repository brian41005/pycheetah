# coding: utf-8
# this is a example for NYT today's paper


import os
import sys


pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pkg_dir)
import pycheetah
# nytimes
all_daily_urls = list(pycheetah.gen_urls('http://www.nytimes.com/indexes/%s/todayspaper/index.html',
                                         '2017/1/1',
                                         '2017/1/1',
                                         date_format='%Y/%m/%d',
                                         product=['date']))
print(all_daily_urls[:3])

# the guardian
Classification = ['world', 'politics', 'sport', 'football', 'culture',
                  'business', 'lifeandstyle', 'fashion', 'environment',
                  'technology', 'travel']
all_daily_urls = list(pycheetah.gen_urls('https://www.theguardian.com/%s/%s/all',
                                         '2010/1/1',
                                         '2017/12/1',
                                         product=[Classification, 'date']))
print(all_daily_urls[:3])
