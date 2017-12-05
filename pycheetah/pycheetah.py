# coding: utf-8
import logging
import os
import threading
from multiprocessing import Process, Queue

from . import utils

__all__ = ['Page', 'start']
CORE = max(1, os.cpu_count())
NUM_THREAD = 15


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
        self.work_result = {}
        self.request = Page.__request__
        for func in Page.__worker__:
            name = func.__name__.replace('get_', '')
            self.workers[name] = func
            self.work_result[name] = None

    def run(self):
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
        return self.is_alive() < other.is_alive()

    def __le__(self, other):
        return self.is_alive() <= other.is_alive()


def __f(args, *, queue=None):
    l, taskManager = args[0], args[1]

    manager = taskManager(l, NUM_THREAD)
    manager.start()
    if queue:
        queue.put(manager.result)
    else:
        return manager.result


# def _map(f, partition):
#     temp_result = []
#     with Pool(processes=CORE) as pool:
#         for i in pool.imap_unordered(f, partition):
#             temp_result.extend(i)
#     return temp_result


def _map(f, partition):
    q = Queue()
    temp_result = []
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
