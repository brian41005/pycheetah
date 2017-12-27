# coding: utf-8
import asyncio
import inspect
import logging
import os
import time

from . import utils
from .base import BaseCheetah
from .command import *
from .map import StrategyMap
from .task import TaskManagerFactory

__all__ = ('Cheetah', 'start', 'AsyncCheetah')


class Cheetah(BaseCheetah):
    concurrent = 5

    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.worker = self.__class__.worker
        self.item = {item_name: None for item_name,
                     _ in self.worker.items()}
        self.item['url'] = self.url

    def run(self):
        request_method = self.request
        resp = request_method(self.url)
        if resp:
            for key, fn in self.worker.items():
                self.item[key] = fn(self, resp)
            return self.item

    def __call__(self):
        try:
            return self.run()
        except Retry:
            return self.url


class AsyncCheetah(BaseCheetah):
    concurrent = 1

    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.item = {item_name: None for item_name,
                     _ in self.__class__.worker.items()}
        self.item['url'] = self.url

    async def run(self):
        worker = self.__class__.worker
        resp = await self.request(self.url)
        if resp:
            for key, fn in worker.items():
                if not asyncio.iscoroutinefunction(fn):
                    fn = asyncio.coroutine(fn)
                    worker.update({key: fn})
                self.item[key] = await fn(self, resp)
            return self.item

    async def __call__(self):
        try:
            return await self.run()
        except Retry:
            return self.url


def start(urls, cheetah, cpu=None, verbose=True):
    cpu = cpu if cpu else os.cpu_count()
    cpu = min(len(urls), cpu)
    t0 = time.time()

    partition = []
    for chunk in utils.partition(urls, cpu):
        manager = TaskManagerFactory.create_taskmanager(
            cheetah.concurrent, chunk, cheetah)
        partition.append(manager)

    result = StrategyMap(cpu=cpu).map(partition)

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
