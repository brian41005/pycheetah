# coding: utf-8
import os
import random
import re
import sys
import time
import unicodedata
import unittest
import asyncio


class TestElse(unittest.TestCase):
    def setUp(self):
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(pkg_dir + '/example')
        import example
        self.example = example

    def test_X(self):
        results = ['1234'] * 50000 + [{}] * 50000
        random.shuffle(results)
        t0 = time.time()
        retry = list(filter(lambda result: type(result) is str, results))
        done = list(filter(lambda result: type(result) is dict, results))
        self.assertLessEqual(time.time() - t0, 0.05)

    def test_theguardian(self):
        for r in self.example.theguardian.main():
            self.assertNotEqual(r, [])

    def test_async_theguardian(self):
        for r in self.example.async_theguardian.main():
            self.assertNotEqual(r, [])

    def test_nytimes(self):
        for r in self.example.nytimes.main():
            self.assertNotEqual(r, [])

    def test_ptt(self):
        for r in self.example.ptt_movie.main():
            self.assertNotEqual(r, [])

    def test_check_asyncfunc(self):
        async def fn():
            pass
        self.assertTrue(asyncio.iscoroutinefunction(fn))

    def test_baseclass_static_attr(self):
        class B:
            attr = None

        class A(B):
            def __init__(self):
                A.attr = 'A'

        class C(B):
            def __init__(self):
                C.attr = 'C'
        self.assertEqual(C().attr, 'C')
        self.assertEqual(A().attr, 'A')
