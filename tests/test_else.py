# coding: utf-8
import functools
import os
import re
import sys
import time
import random
import unicodedata
import unittest
from collections import deque
from multiprocessing import Pool, Process


class TestElse(unittest.TestCase):
    def test_X(self):
        results = ['1234'] * 50000 + [{}] * 50000
        random.shuffle(results)
        t0 = time.time()
        retry = list(filter(lambda result: type(result) is str, results))
        done = list(filter(lambda result: type(result) is dict, results))
        self.assertLessEqual(time.time() - t0, 0.05)
