# coding: utf-8
import logging
import os
import time

from . import utils
from .base import BaseCheetah
from .command import Retry, Fail
from .map import StrategyMap
from .task import TaskManagerFactory

__all__ = ('Cheetah', 'start', 'AsyncCheetah')


class Cheetah(BaseCheetah):
    concurrent = 5

    def run(self):
        resp = self.request(self.url)
        if resp:
            for key, fn in self.worker.fn_items():
                self.item[key] = fn(self, resp)
            return self.item

    def __call__(self):
        try:
            return self.run()
        except Retry:
            return self.url
        except Fail:
            pass


class AsyncCheetah(BaseCheetah):
    concurrent = 1

    async def run(self):
        resp = await self.request(self.url)
        if resp:
            for key, fn in self.worker.fn_items(asyn=True):
                self.item[key] = await fn(self, resp)
            return self.item

    async def __call__(self):
        try:
            return await self.run()
        except Retry:
            return self.url
        except Fail:
            pass


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
