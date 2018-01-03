import asyncio
from abc import ABCMeta, abstractmethod

from . import log

__all__ = ['BaseCheetah', 'Worker']


class Worker(dict):

    def addfn(self, fn):
        if callable(fn):
            fn_name = fn.__name__
            self[fn_name] = fn
        else:
            raise TypeError('{} is not callable'.format(fn))

    def __getattr__(self, name):
        return self[name]

    def fn_items(self, asyn=False):
        for key, fn in self.items():
            if asyn and not asyncio.iscoroutinefunction(fn):
                fn = asyncio.coroutine(fn)
            yield key, fn


class BaseCheetah:
    worker = None

    def __new__(cls, name, url):
        if not cls.worker:
            cls.worker = Worker()
            for func_str in (set(dir(cls)) - set(dir(BaseCheetah))):
                func = getattr(cls, func_str)
                if callable(func):
                    if func.__name__.startswith('get_'):
                        func.__name__ = func.__name__.replace('get_', '')
                        cls.worker.addfn(log.addLogger(func))

        return super().__new__(cls)

    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.worker = self.__class__.worker
        self.item = {key: None for key in self.worker.keys()}
        self.item['url'] = self.url

    @abstractmethod
    def request(self, url):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def __call__(self):
        pass
