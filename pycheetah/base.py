import asyncio
from abc import ABCMeta, abstractmethod

from . import log

__all__ = ('BaseCheetah', 'Worker')


class Worker(dict):

    def addfn(self, fn):
        if callable(fn):
            fn_name = fn.__name__
            self[fn_name] = fn
        else:
            raise TypeError('fn is not callable')

    def __getattr__(self, name):
        return self[name]

    def fn_items(self, asyn=False):
        if not asyn:
            for key, fn in self.items():
                yield key, fn
        else:
            for key, fn in self.items():
                if not asyncio.iscoroutinefunction(fn):
                    fn = asyncio.coroutine(fn)
                    self[key] = fn
                yield key, fn


class BaseCheetah:
    worker = None
    request = None

    def __new__(cls, *agrs):

        if not cls.worker:
            cls.worker = Worker()
            for func_str in (set(dir(cls)) - set(dir(BaseCheetah))):
                func = getattr(cls, func_str)
                if callable(func):
                    if func.__name__.startswith('get_'):
                        func.__name__ = func.__name__.replace('get_', '')
                        cls.worker.addfn(log.addLogger(func))
                    elif func.__name__ == 'request':
                        cls.request = log.addLogger(func)

            if not cls.request:
                raise NotImplementedError('request method not found!')

        return super(BaseCheetah, cls).__new__(cls)

    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.worker = self.__class__.worker
        self.item = {item_name: None for item_name,
                     _ in self.worker.items()}
        self.item['url'] = self.url

    def run(self):
        pass

    @abstractmethod
    def __call__(self):
        pass
