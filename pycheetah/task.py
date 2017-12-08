import logging
import time
from abc import ABC, ABCMeta, abstractmethod
from concurrent import futures
from queue import PriorityQueue

from .container import Result
__all__ = ['DefaultTaskManager']


class ABCTaskManager(metaclass=ABCMeta):

    @abstractmethod
    def start(self):
        pass


class DefaultTaskManager(ABCTaskManager):
    def __init__(self, urls, cheetah, num_thread=1):
        self.urls = urls
        self.cheetah_class = cheetah
        self.num_thread = min(len(self.urls), num_thread)

    def __submit(self, executor, iterated_obj):
        to_do = [executor.submit(self.cheetah_class('', url))
                 for url in self.urls]
        results = [future.result() for future in futures.as_completed(to_do)]

        retry = list(filter(lambda result: isinstance(
            result, self.cheetah_class), results))
        done = list(filter(lambda result: type(result) is dict, results))
        # logging.info(retry)
        return retry, done

    def start(self):
        results = []
        with futures.ThreadPoolExecutor(self.num_thread) as executor:
            retry_to_do, done = self.__submit(executor, self.urls)

            results.extend(done)
            while retry_to_do:
                logging.info('retry %d cheetah' % (len(retry_to_do)))
                retry_to_do, done = self.__submit(executor, retry_to_do)
                results.extend(done)

        return Result(results)
