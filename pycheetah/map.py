import concurrent.futures
from functools import wraps
from multiprocessing import Process, Queue
from sys import platform

from .datamodel import Result

__all__ = ['_map', '_map_macos', 'StrategyMap']


def return2queue(fn):
    @wraps(fn)
    def func_wrapper(*args, queue):
        result_obj = fn(*args)
        queue.put(result_obj)
    return func_wrapper


def _map(fn, partition):
    temp_result = Result()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for res_obj in executor.map(fn, partition):
            temp_result.extend(res_obj)
    return temp_result


def _map_macos(fn, partition):
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
    def __init__(self):
        self.__map = _map_macos if platform == 'darwin' else _map

    def map(self, *args, **kwargs):
        return self.__map(*args, **kwargs)
