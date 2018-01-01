import asyncio
import logging
import time
from abc import ABC, abstractmethod
from concurrent import futures

from .container import Result
from .utils import partition

__all__ = ('TaskManagerFactory',)


class ABCTaskManager(ABC):

    @abstractmethod
    def _submit(self, iterable):
        pass

    @abstractmethod
    def start(self):
        pass

    def _differentiate(self, result):
        to_do, done = [], []
        for item in result:
            if isinstance(item, str):
                to_do.append(item)
            elif isinstance(item, dict):
                done.append(item)

        logging.info('[{}] done, [{}] urls need to be resubmited'.format(
            len(done), len(to_do)))
        return to_do, done

    def _start(self, iterable):
        result_obj = Result()
        result = self._submit(iterable)
        to_do, done = self._differentiate(result)
        result_obj.extend(done)

        while to_do:
            result = self._submit(to_do)
            to_do, done = self._differentiate(result)
            result_obj.extend(done)

        return result_obj


class AsyncTaskManager(ABCTaskManager):

    def __init__(self, urls, cheetah):
        self.urls = urls
        self.cheetah_cls = cheetah

    def start(self):
        return self._start(self.urls)

    def _submit(self, iterable):
        logging.info('submitting {} urls'.format(len(iterable)))
        loop = asyncio.new_event_loop()  # instead of get_event_loop
        result_obj = Result()

        tasks = []
        for i, each in enumerate(self.urls):
            task = loop.create_task(self.cheetah_cls(str(i), each)())
            tasks.append(task)

        wait_coro = asyncio.wait(tasks)
        res, q = loop.run_until_complete(wait_coro)

        for task in res:
            result_obj.append(task.result())

        loop.close()
        return result_obj


class ThreadTaskManager(ABCTaskManager):

    def __init__(self, urls, cheetah, num_thread=5):
        self.urls = urls
        self.cheetah_cls = cheetah
        self.num_thread = min(len(self.urls), num_thread)

    def start(self):
        return self._start(self.urls)

    def _submit(self, iterable):
        logging.info('submitting {} urls'.format(len(iterable)))

        with futures.ThreadPoolExecutor(self.num_thread) as executor:
            to_do = [executor.submit(self.cheetah_cls(str(i), each))
                     for i, each in enumerate(iterable)]

            result = [future.result()
                      for future in futures.as_completed(to_do)]
        return result


class TaskManagerFactory:

    @staticmethod
    def create_taskmanager(concurrent, iterable, cheetah):
        if concurrent > 1:
            return ThreadTaskManager(iterable, cheetah)
        elif concurrent == 1:
            return AsyncTaskManager(iterable, cheetah)
        else:
            raise ValueError(
                'concurrent should be > 0, {%d} given '.format(concurrent))
