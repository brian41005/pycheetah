# coding: utf-8
import logging
import threading
from bs4 import BeautifulSoup
import requests


class Worker(threading.Thread):
    __slots__ = ['soup', 'func', 'args', 'kwargs', '_result']

    def __init__(self, name, func):
        super(Worker, self).__init__(name=name, daemon=True)
        self.func = func
        self.args = None
        self.kwargs = None
        self._result = None

    def start(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super(Worker, self).start()

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            if result:
                self._result = result
        except Exception as msg:
            logging.exception(msg)

    def join(self):
        super(Worker, self).join()
        return self._result


class Page(threading.Thread):
    def __init__(self, name, url):
        super(Page, self).__init__(name=name, daemon=True)
        self.url = url
        self.worker_list = []
        self.request_method = None
        for func_str in (set(dir(self.__class__)) - set(dir(Page))):
            func = getattr(self, func_str)
            if func.__name__.startswith('get_') and callable(func):
                self.worker_list.append(
                    Worker(func.__name__.replace('get_', ''), func))
            if func.__name__ == 'request' and callable(func):
                self.request_method = func
        if not self.request_method:
            raise NotImplementedError('request method not found!')

        self.work_result = {}

    def run(self):
        response = self.request_method(self.url)
        for worker in self.worker_list:
            worker.start(response)

    def join(self):
        super(Page, self).join()
        for worker in self.worker_list:
            self.work_result[worker.name] = worker.join()
        return self.work_result
