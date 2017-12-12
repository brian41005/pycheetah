# coding: utf-8
from .cscsaver import ISaver
__all__ = ['Result']


class Result(list, ISaver):
    def reduce_key(self, key):
        result = []
        for i in self:
            result.extend(i[key])
        return result

    def save(self, file=None):
        pass
