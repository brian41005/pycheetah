import logging
import time
from abc import ABC, abstractmethod
from concurrent import futures

from .container import Result

__all__ = ['DefaultTaskManager']


class ABCTaskManager(ABC):

    @abstractmethod
    def start(self):
        pass


class DefaultTaskManager(ABCTaskManager):

    def __init__(self, urls, cheetah, num_thread=1):
        self.urls = urls
        self.cheetah_cls = cheetah
        self.num_thread = min(len(self.urls), num_thread)

    def __submit(self, executor, iterable):
        logging.info('start submit {} urls'.format(len(iterable)))
        to_do = [executor.submit(self.cheetah_cls(str(i), each))
                 for i, each in enumerate(iterable)]

        retry, done = [], []
        for future in futures.as_completed(to_do):
            res = future.result()
            if isinstance(res, str):
                retry.append(res)
            elif isinstance(res, dict):
                done.append(res)

        logging.info('[{}] done, [{}] urls need to be resubmited'.format(
            len(done), len(retry)))
        return retry, done

    def start(self):
        results = Result()
        with futures.ThreadPoolExecutor(self.num_thread) as executor:
            to_do, done = self.__submit(executor, self.urls)
            results.extend(done)

            while to_do:
                to_do, done = self.__submit(executor, to_do)
                results.extend(done)

        return results
