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


pkg_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(pkg_dir)
import pycheetah

all_daily_urls = [i for i in pycheetah.gen_urls('2010/1/1',
                                                '2017/12/1',
                                                Classification)]
