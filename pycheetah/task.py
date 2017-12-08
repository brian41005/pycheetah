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
        self.cheetah = cheetah
        self.num_thread = min(len(self.urls), num_thread)

    def __submit(self, executor, iterated_obj):
        to_do = []

        for url in self.urls:
            to_do.append(executor.submit(self.cheetah('', url)))
        return to_do

    def start(self):
        with futures.ThreadPoolExecutor(self.num_thread) as executor:
            to_do = self.__submit(executor, self.urls)
            logging.info('submit completed')
            result = [future.result()
                      for future in futures.as_completed(to_do)]
        return Result(result)
