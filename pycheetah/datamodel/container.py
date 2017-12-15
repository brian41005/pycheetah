# coding: utf-8
import csv

from .cscsaver import ISaver

__all__ = ['Result']


class Result(list, ISaver):
    def reduce_key(self, key):
        result = []
        for i in self:
            result.extend(i[key])
        return result

    def save(self, *args, **kwargs):
        default_kwargs = {'encoding': 'utf-8', 'newline': '\n', 'mode': 'w'}
        default_kwargs.update(kwargs)
        with open(*args, **default_kwargs) as csvfile:
            fieldnames = list(self.__getitem__(0).keys())
            writer = csv.DictWriter(csvfile,
                                    fieldnames=fieldnames,
                                    delimiter=',',
                                    quoting=csv.QUOTE_ALL)

            writer.writeheader()
            writer.writerows(self)
