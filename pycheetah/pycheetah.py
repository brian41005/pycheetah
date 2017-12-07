# coding: utf-8
import logging
import os
import threading
import random
import time
from multiprocessing import Process, Queue

import concurrent.futures
from . import utils
from .container import Result
from .task import *

__all__ = ['Cheetah', 'start']
NUM_THREAD = 20


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
        # super(Cheetah, self).__init__(name=name, daemon=True)
        self.url = url
        self.work_result = {}
        for func_name, _ in Cheetah.__workers__.items():
            self.work_result[func_name] = None
        self.started_time = time.time()

    def __call__(self):
        # time.sleep(random.random())
        self.started_time = time.time()
        try:
            response = Cheetah.__request__(self, self.url)
            if response:
                for worker_name, worker in Cheetah.__workers__.items():
                    self.work_result[worker_name] = worker(self, response)
                logging.info('[%s]' % (self.url))
        except Exception as msg:
            logging.error('%s [%s]' % (msg, self.url))

        return self.work_result

    def start(self):
        if hasattr(self, '__call__'):
            return self.__call__()
        elif hasattr(self, 'run'):
            return self.run()

    def retry(self, credit=3):
        self.start()

    def join(self, *args, **kwargs):
        # super(Cheetah, self).join(*args, **kwargs)
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


def _map(f, partition):
    # q = Queue()
    temp_result = Result()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for res_obj in executor.map(f, partition):
            temp_result.extend(res_obj)
    return temp_result


def start(urls, cheetah, cpu=os.cpu_count()):
    _partition = [(chunk, cheetah) for chunk in utils.partition(urls, cpu)]
    return _map(__f, _partition)
