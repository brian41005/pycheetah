# coding: utf-8
import itertools
import logging
import os
import threading
import time
from collections import defaultdict
from functools import total_ordering
from multiprocessing import Pool

from . import utils

__all__ = ['Page', 'start']
CORE = os.cpu_count() if os.cpu_count() else 1
NUM_THREAD = 25


class Page(threading.Thread):
    __worker__ = []
    __request__ = None

    def __new__(cls, *args, **kwargs):
        for func_str in (set(dir(cls)) - set(dir(Page))):
            func = getattr(cls, func_str)
            if func.__name__.startswith('get_') and callable(func):
                Page.__worker__.append(func)
            if func.__name__ == 'request' and callable(func):
                Page.__request__ = func
        if not Page.__request__ and not callable(Page.__request__):
            raise NotImplementedError('request method not found!')
        return super(Page, cls).__new__(cls)

    def __init__(self, name, url):
        super(Page, self).__init__(name=name, daemon=True)
        self.url = url
        self.workers = {}
        self.work_result = defaultdict(None)
        self.request = Page.__request__
        for func in Page.__worker__:
            name = func.__name__.replace('get_', '')
            self.workers[name] = func

    def run(self):
        try:
            response = self.request(self.url)
            if response:
                for name, worker in self.workers.items():
                    self.work_result[name] = worker(response)
        except Exception as msg:
            logging.error(msg)

    def join(self):
        super(Page, self).join()
        return self.work_result

    def is_alive(self):
        return super(Page, self).is_alive()

    def __lt__(self, other):
        return self.is_alive() < other.is_alive()

    def __le__(self, other):
        return self.is_alive() <= other.is_alive()


def __f(args):
    l, taskManager = args
    ts = time.time()
    manager = taskManager(l, NUM_THREAD)
    manager.start()
    return manager.result


def start(urls, page_class):
    _partition = [(i, page_class) for i in utils.partition(urls, CORE)]
    with Pool(CORE) as p:
        temp_result = list(itertools.chain(*p.map(__f, _partition)))
    return temp_result
