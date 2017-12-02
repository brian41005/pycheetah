# coding: utf-8
import logging
import threading


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
    __worker__ = []
    __request__ = None

    def __new__(cls, *args, **kwargs):
        for func_str in (set(dir(cls)) - set(dir(Page))):
            func = getattr(cls, func_str)
            if func.__name__.startswith('get_') and callable(func):
                Page.__worker__.append(func)
            if func.__name__ == 'request' and callable(func):
                Page.__request__ = func
        return super(Page, cls).__new__(cls)

    def __init__(self, name, url):
        super(Page, self).__init__(name=name, daemon=True)
        self.url = url
        self.worker_list = []
        self.request = Page.__request__
        for func in Page.__worker__:
            name = func.__name__.replace('get_', '')
            self.worker_list.append(Worker(name, func))

        if not self.request:
            raise NotImplementedError('request method not found!')
        self.work_result = {}

    def run(self):
        response = self.request(self.url)
        for worker in self.worker_list:
            worker.start(response)

    def join(self):
        super(Page, self).join()
        for worker in self.worker_list:
            self.work_result[worker.name] = worker.join()
        return self.work_result
