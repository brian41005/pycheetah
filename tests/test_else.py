# coding: utf-8
import os
import random
import re
import sys
import time
import unicodedata
import unittest


class TestElse(unittest.TestCase):
    def test_X(self):
        results = ['1234'] * 50000 + [{}] * 50000
        random.shuffle(results)
        t0 = time.time()
        retry = list(filter(lambda result: type(result) is str, results))
        done = list(filter(lambda result: type(result) is dict, results))
        self.assertLessEqual(time.time() - t0, 0.05)

    def test_theguardian(self):
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(pkg_dir + '/example')
        import example.theguardian
        example.theguardian.main
