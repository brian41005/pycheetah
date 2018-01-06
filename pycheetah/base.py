import asyncio
import logging
import os
import time
from abc import abstractmethod

from . import log, utils
from .map import StrategyMap
from .task import TaskManagerFactory

__all__ = ['BaseCheetah', 'Worker']


class Worker(dict):

    def addfn(self, fn):
        if callable(fn):
            fn_name = fn.__name__
            self[fn_name] = fn
        else:
            raise TypeError('{} is not callable'.format(fn))

    def __getattr__(self, name):
        return self[name]

    def fn_items(self, asyn=False):
        for key, fn in self.items():
            if asyn and not asyncio.iscoroutinefunction(fn):
                fn = asyncio.coroutine(fn)
            yield key, fn


class BaseCheetah:
    worker = None
    concurrent = 1

    def __new__(cls, name, url):
        if not cls.worker:
            cls.worker = Worker()
            for func_str in (set(dir(cls)) - set(dir(BaseCheetah))):
                func = getattr(cls, func_str)
                if callable(func):
                    if func.__name__.startswith('get_'):
                        func.__name__ = func.__name__.replace('get_', '')
                        cls.worker.addfn(log.addLogger(func))

        return super().__new__(cls)

    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.worker = self.__class__.worker
        self.item = {key: None for key in self.worker.keys()}
        self.item['url'] = self.url

    @classmethod
    def start(cls, urls, cpu=None, verbose=True):
        cpu = cpu if cpu else os.cpu_count()
        cpu = min(len(urls), cpu)
        t0 = time.time()

        partitions = [TaskManagerFactory.create(cls, chunk)
                      for chunk in utils.partition(urls, cpu)]
        result = StrategyMap(cpu=cpu).map(partitions)

        cost_time = time.time() - t0
        num_of_item = len(result)
        try:
            avg = cost_time / num_of_item
        except ZeroDivisionError:
            avg = 0
        if verbose:
            logging.info('spent:{:4.2f}s ({:3.2f}hr), avg:{:.6f}s, [{:d}] data'
                         .format(cost_time,
                                 cost_time / 3600,
                                 avg,
                                 num_of_item))

        return result

    @abstractmethod
    def request(self, url):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def __call__(self):
        pass
