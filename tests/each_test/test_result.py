# coding: utf-8
import os
import re
import sys
import time
import unicodedata
import unittest
from collections import deque
from multiprocessing import Process, Pool

import requests
from bs4 import BeautifulSoup
pkg_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pkg_dir)
import pycheetah


r = pycheetah.Result([{'url': [1]}])
r2 = pycheetah.Result([{'url': [2, 3]}])
r.extend(r2)
print(r[0])
