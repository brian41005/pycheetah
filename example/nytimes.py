# coding: utf-8
# this is a example for NYT today's paper

import itertools
import os
import re
import sys
import time
import unicodedata

import requests
from bs4 import BeautifulSoup


pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pkg_dir)
import pycheetah

all_daily_urls = list(pycheetah.gen_urls('http://www.nytimes.com/indexes/%s/todayspaper/index.html',
                                         '2017/1/1',
                                         '2017/1/5',
                                         date_format='%Y/%m/%d',
                                         product=['date']))
