# coding: utf-8

from .base import BaseCheetah
from .command import Fail, Retry

__all__ = ['Cheetah', 'AsyncCheetah']


class Cheetah(BaseCheetah):
    concurrent = 5

    def run(self):
        resp = self.request(self.url)
        if resp:
            for key, fn in self.worker.fn_items():
                self.item[key] = fn(self, resp)
            return self.item

    def __call__(self):
        try:
            return self.run()
        except Retry:
            return self.url
        except Fail:
            pass


class AsyncCheetah(BaseCheetah):
    concurrent = 1

    async def run(self):
        resp = await self.request(self.url)
        if resp:
            for key, fn in self.worker.fn_items(asyn=True):
                self.item[key] = await fn(self, resp)
            return self.item

    async def __call__(self):
        try:
            return await self.run()
        except Retry:
            return self.url
        except Fail:
            pass
