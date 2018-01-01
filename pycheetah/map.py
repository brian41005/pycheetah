import concurrent.futures
import logging
from functools import wraps
from multiprocessing import Process, Queue
from sys import platform

from .container import Result

__all__ = ('StrategyMap',)


def _fn(task_manager):
    return task_manager.start()


def return2queue(fn):
    @wraps(fn)
    def func_wrapper(*args, queue):
        result_obj = fn(*args)
        queue.put(result_obj)
    return func_wrapper


def _map_single_cpu(fn, partition):
    logging.info(len(partition))
    temp_result = Result()
    for res_obj in map(fn, partition):
        temp_result.extend(res_obj)
    return temp_result


def _map(fn, partition):
    temp_result = Result()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for res_obj in executor.map(fn, partition):
            temp_result.extend(res_obj)
    return temp_result


def _map_macos(fn, partition):
    '''
    temp solution
    '''
    q = Queue()
    temp_result = Result()
    fn = return2queue(fn)
    jobs = [Process(target=fn,
                    daemon=True,
                    args=(each_part,),
                    kwargs={'queue': q})

            for each_part in partition]

    for j in jobs:
        j.start()
    for i in range(len(partition)):
        temp_result.extend(q.get())
    for j in jobs:
        j.join()
    return temp_result


class StrategyMap:
    def __init__(self, *, cpu):
        logging.info('using {} cpu'.format(cpu))
        if cpu > 1:
            self.__map = _map_macos if platform == 'darwin' else _map
        else:
            self.__map = _map_single_cpu

    def map(self, iterable_obj, **kwargs):
        return self.__map(_fn, iterable_obj)
