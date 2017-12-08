# coding: utf-8
import concurrent.futures
import logging
import os
import random
import threading
import time
from multiprocessing import Process, Queue

from . import utils
from .container import Result
from .map import StrategyMap
from .task import *

__all__ = ['Cheetah', 'start']
NUM_THREAD = 5


class Cheetah:
    __workers__ = {}
    __request__ = None

    def __new__(cls, *args, **kwargs):
        for func_str in (set(dir(cls)) - set(dir(Cheetah))):
            func = getattr(cls, func_str)
            if func.__name__.startswith('get_') and callable(func):
                name = func.__name__.replace('get_', '')
                Cheetah.__workers__[name] = func
            elif func.__name__ == 'request' and callable(func):
                Cheetah.__request__ = func

        if not Cheetah.__request__ and not callable(Cheetah.__request__):
            raise NotImplementedError('request method not found!')

        return super(Cheetah, cls).__new__(cls)

    def __init__(self, name, url):
        self.url = url
        self.work_result = {}
        # for func_name, _ in Cheetah.__workers__.items():
        #     self.work_result[func_name] = None
        self.started_time = time.time()

    def run(self):
        self.started_time = time.time()
        try:
            response = Cheetah.__request__(self, self.url)
            if response:
                for worker_name, worker in Cheetah.__workers__.items():
                    self.work_result[worker_name] = worker(self, response)
                return self.work_result

        except Exception as msg:
            logging.error('%s [%s]' % (msg, self.url))
        return self

    def __call__(self):
        return self.run()

    def start(self):
        return self.run()

    def retry(self, credit=3):
        self.start()

    def join(self, *args, **kwargs):
        return self.work_result

    def __lt__(self, other):
        return (self.started_time < other.started_time)

    def __le__(self, other):
        return (self.started_time <= other.started_time)


def __f(*args, queue=None):
    chunk, cheetah = args[0]
    manager = DefaultTaskManager(chunk, cheetah, NUM_THREAD)
    result_obj = manager.start()
    if queue:
        queue.put(result_obj)
    else:
        return result_obj


def start(urls, cheetah, cpu=os.cpu_count()):
    cpu = min(len(urls), cpu)
    _partition = [(chunk, cheetah) for chunk in utils.partition(urls, cpu)]
    map_obj = StrategyMap()
    return map_obj.map(__f, _partition)
