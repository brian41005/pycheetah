# coding: utf-8
import logging
import os
import threading
import time
from multiprocessing import Process, Queue

from . import utils
from .container import Result

__all__ = ['Page', 'start']
CORE = max(1, os.cpu_count())
NUM_THREAD = 15


class Page(threading.Thread):
    __worker__ = []
    __request__ = None

    @classmethod
    def __get_subclass_method(self):
        for func_str in (set(dir(self)) - set(dir(Page))):
            func = getattr(self, func_str)
            if func.__name__.startswith('get_') and callable(func):
                Page.__worker__.append(func)
            if func.__name__ == 'request' and callable(func):
                Page.__request__ = func
        if not Page.__request__ and not callable(Page.__request__):
            raise NotImplementedError('request method not found!')

    def __new__(cls, *args, **kwargs):
        cls.__get_subclass_method()
        return super(Page, cls).__new__(cls)

    def __init__(self, name, url):
        super(Page, self).__init__(name=name, daemon=True)
        self.url = url
        self.workers = {}
        self.work_result = {}
        self.request = Page.__request__
        for func in Page.__worker__:
            name = func.__name__.replace('get_', '')
            self.workers[name] = func
            self.work_result[name] = None

    def started_time(self):
        return self.started

    def run(self):
        self.started = time.time()
        try:
            response = self.request(self.url)
            if response:
                for name, worker in self.workers.items():
                    self.work_result[name] = worker(response)
        except Exception as msg:
            logging.error('%s [%s]' % (msg, self.url))

    def join(self, *args, **kwargs):
        super(Page, self).join(*args, **kwargs)
        return self.work_result

    def __lt__(self, other):
        return ((self.started, self.is_alive()) <
                (other.started_time(), other.is_alive()))

    def __le__(self, other):
        return ((self.started, self.is_alive()) <=
                (other.started_time(), other.is_alive()))


def __f(args, *, queue=None):
    l, taskManager = args[0], args[1]

    manager = taskManager(l, NUM_THREAD)
    result_obj = manager.start()
    if queue:
        queue.put(result_obj)
    else:
        return result_obj


def _map(f, partition):
    q = Queue()
    temp_result = Result()
    jobs = [Process(target=__f, daemon=True,
                    args=(p,), kwargs={'queue': q})
            for p in partition]

    for j in jobs:
        j.start()
    for i in range(CORE):
        temp_result.extend(q.get())
    for j in jobs:
        j.join()
    return temp_result


def start(urls, page_class):
    _partition = [(i, page_class) for i in utils.partition(urls, CORE)]
    return _map(__f, _partition)
