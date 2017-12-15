# coding: utf-8
import logging
import os
import time

from . import utils
from .map import StrategyMap
from .task import DefaultTaskManager

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
                Cheetah.__workers__[name] = utils.addLogger(func)
            elif func.__name__ == 'request' and callable(func):
                Cheetah.__request__ = utils.addLogger(func)

        if not Cheetah.__request__ and not callable(Cheetah.__request__):
            raise NotImplementedError('request method not found!')

        return super(Cheetah, cls).__new__(cls)

    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.item = {item_name: None for item_name,
                     _ in Cheetah.__workers__.items()}
        self.item['url'] = self.url
        self.started_time = time.time()

    def __run(self):
        self.started_time = time.time()
        response = Cheetah.__request__(self, self.url)
        if response == self.url:
            return response
        elif response:
            for item_name, worker in Cheetah.__workers__.items():
                self.item[item_name] = worker(self, response)
            return self.item

    def __call__(self):
        return self.__run()

    def start(self):
        return self.__run()

    def retry(self):
        logging.info('RETRY [{:80s}]'.format(self.name + '|' + self.url))
        return self.url

    def join(self, *args, **kwargs):
        return self.item

    def __lt__(self, other):
        return (self.started_time < other.started_time)

    def __le__(self, other):
        return (self.started_time <= other.started_time)


def _fn(task_manager):
    return task_manager.start()


def start(urls, cheetah, cpu=None, verbose=True):
    cpu = cpu if cpu else os.cpu_count()
    cpu = min(len(urls), cpu)
    partition = [DefaultTaskManager(chunk, cheetah, NUM_THREAD)
                 for chunk in utils.partition(urls, cpu)]
    t0 = time.time()
    result = StrategyMap().map(_fn, partition)

    cost_time = time.time() - t0
    num_of_item = len(result)
    avg = cost_time / num_of_item
    logging.info('spent:{:4.2f}s ({:3.2f}hr), avg:{:.6f}, [{:d}] data'.format(
        cost_time, cost_time / 3600, avg, num_of_item))

    return result
