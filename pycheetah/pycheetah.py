# coding: utf-8
import logging
import os
import time
import asyncio
from . import utils
from .base import BaseCheetah
from .map import StrategyMap
from .task import DefaultTaskManager, AsyncTaskManager

__all__ = ['Cheetah', 'start', 'AsyncCheetah']


class Cheetah(BaseCheetah):
    thread = True

    def __init__(self, name, url):
        self.url = url
        self.name = name
        worker_methods = self.__class__.__workers__
        self.item = {item_name: None for item_name,
                     _ in worker_methods.items()}
        self.item['url'] = self.url
        self.started_time = time.time()

    def run(self):
        self.started_time = time.time()
        request_method = self.__class__.__request__
        response = request_method(self, self.url)
        if response == self.url:
            return response
        elif response:
            worker_methods = self.__class__.__workers__
            for item_name, worker in worker_methods.items():
                self.item[item_name] = worker(self, response)
            return self.item

    def __call__(self):
        return self.run()


class AsyncCheetah(BaseCheetah):
    thread = False

    def __init__(self, name, url):
        self.url = url
        self.name = name
        worker_methods = self.__class__.__workers__
        self.item = {item_name: None for item_name,
                     _ in worker_methods.items()}
        self.item['url'] = self.url
        self.started_time = time.time()

    async def run(self):
        self.started_time = time.time()
        request_method = asyncio.coroutine(self.__class__.__request__)

        response = await request_method(self, self.url)
        if response == self.url:
            return response
        elif response:
            worker_methods = self.__class__.__workers__
            for item_name, worker in worker_methods.items():
                worker = asyncio.coroutine(worker)
                self.item[item_name] = await worker(self, response)
            return self.item

    async def __call__(self):
        return await self.run()


def start(urls, cheetah, cpu=None, verbose=True):
    cpu = cpu if cpu else os.cpu_count()
    cpu = min(len(urls), cpu)
    t0 = time.time()
    if not cheetah.thread:
        partition = [AsyncTaskManager(chunk, cheetah)
                     for chunk in utils.partition(urls, cpu)]
        result = StrategyMap(thread=False).map(partition)
    else:

        partition = [DefaultTaskManager(chunk, cheetah)
                     for chunk in utils.partition(urls, cpu)]
        result = StrategyMap().map(partition)

    cost_time = time.time() - t0
    num_of_item = len(result)
    try:
        avg = cost_time / num_of_item
    except ZeroDivisionError:
        avg = 0
    if verbose:
        logging.info('spent:{:4.2f}s ({:3.2f}hr), avg:{:.6f}s, [{:d}] data'.format(
            cost_time, cost_time / 3600, avg, num_of_item))

    return result
