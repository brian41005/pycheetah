# coding: utf-8
import os
import re
import sys
import time
import unicodedata
import unittest
from collections import deque
from multiprocessing import Process, Pool
import functools

import requests
from bs4 import BeautifulSoup
pkg_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pkg_dir)
import pycheetah


class TestResult(unittest.TestCase):
    def setUp(self):
        self.r = pycheetah.Result()

    def test_apped(self):
        self.r.append({'a': 1, 'b': 1})

    def test_extend(self):
        r2 = pycheetah.Result({'a': 2, 'b': 2})
        self.r.extend(r2)

    def test_save1(self):
        self.r.append({'a': 1, 'b': 1})
        self.r.save('test1.csv', mode='w', encoding='utf-8', newline=None)
        self.r.save('test1.csv', mode='a')

    def test_save2(self):
        self.r.append({'a': 1, 'b': 1})
        self.r.append({'a': None, 'b': 2})
        self.r.save('test2.csv')

    def test_save3(self):
        self.r.append({'a': 1, 'b': []})
        self.r.append({'a': 1, 'b': [None]})
        self.r.append({'a': 1, 'b': [1, 2, 3]})
        self.r.save('test3.csv')

    def test_reduceby1(self):
        self.r.append({'a': 1, 'b': 1})
        self.r.append({'a': 1, 'b': 2})
        result = self.r.reduce_by('a')
        self.assertEqual([1, 1], result)

    def test_reduceby2(self):
        self.r.append({'a': [1], 'b': 1})
        self.r.append({'a': None, 'b': 2})
        result = self.r.reduce_by('a')
        self.assertEqual([1, None], result)

    def tearDown(self):
        csv_list = [i for i in os.listdir(os.getcwd()) if i.find('.csv') != -1]
        for csvfile in csv_list:
            os.remove(csvfile)
            pass
