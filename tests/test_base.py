# coding: utf-8
import os
import random
import re
import sys
import time
import unicodedata
import unittest
import asyncio
pkg_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pkg_dir)
import pycheetah


class TestWorker(unittest.TestCase):

    def test_worker_eq(self):
        def fn1():
            pass

        def fn2():
            pass
        w1 = pycheetah.Worker()
        w2 = pycheetah.Worker()
        w1.addfn(fn1)
        w2.addfn(fn2)
        self.assertNotEqual(w1, w2)
        w1 = pycheetah.Worker()
        w2 = pycheetah.Worker()
        w1.addfn(fn1)
        w2.addfn(fn1)
        self.assertEqual(w1, w2)

    def test_worker_attr(self):
        def fn1():
            pass

        def fn2():
            pass
        w1 = pycheetah.Worker()
        w1.addfn(fn1)
        w1.addfn(fn2)
        self.assertEqual(w1.fn1, fn1)
        self.assertEqual(w1.fn2, fn2)
