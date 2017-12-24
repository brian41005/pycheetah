# coding: utf-8
import asyncio
import inspect
import logging
import os
import time

from . import utils
from .base import BaseCheetah
from .map import StrategyMap
from .task import TaskManagerFactory

__all__ = ['Cheetah', 'start', 'AsyncCheetah']


class Cheetah(BaseCheetah):
    thread = 5

    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.worker = self.__class__.worker
        self.item = {item_name: None for item_name,
                     _ in self.worker.items()}
        self.item['url'] = self.url
        self.started_time = time.time()

    def run(self):
        self.started_time = time.time()
        request_method = self.request
        resp = request_method(self.url)

        if resp == self.url:
            return resp
        elif resp:
            for key, fn in self.worker.items():
                self.item[key] = fn(self, resp)
            return self.item

    def __call__(self):
        return self.run()

    def retry(self):
        logging.info('RETRY [{:80s}]'.format(self.name + '|' + self.url))
        return self.url


class AsyncCheetah(BaseCheetah):
    thread = False

    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.item = {item_name: None for item_name,
                     _ in self.__class__.worker.items()}
        self.item['url'] = self.url
        self.started_time = time.time()

    async def run(self):
        self.started_time = time.time()
        worker = self.__class__.worker
        resp = await self.request(self.url)
        if resp == self.url:
            return resp
        elif resp:
            for key, fn in worker.items():
                if not asyncio.iscoroutinefunction(fn):
                    fn = asyncio.coroutine(fn)
                self.item[key] = await fn(self, resp)
            return self.item

    async def __call__(self):
        return await self.run()

    def retry(self):
        logging.info('RETRY [{:80s}]'.format(self.name + '|' + self.url))
        return self.url


def start(urls, cheetah, cpu=None, verbose=True):
    cpu = cpu if cpu else os.cpu_count()
    cpu = min(len(urls), cpu)
    t0 = time.time()

    partition = []
    for chunk in utils.partition(urls, cpu):
        manager = TaskManagerFactory.create_taskmanager(
            cheetah.thread,
            chunk,
            cheetah)
        partition.append(manager)

    result = StrategyMap(is_concurrent=cpu).map(partition)

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
