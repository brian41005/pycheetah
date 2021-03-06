# coding: utf-8
import csv
from abc import ABC, abstractmethod

__all__ = ['Result']


class ISaver(ABC):

    @abstractmethod
    def save(self, file):
        pass


class Result(list, ISaver):
    def reduce_by(self, key):
        result = []
        for item in self:
            if key not in item:
                raise KeyError('\'{}\''.format(key))
            if type(item[key]) is list:
                result.extend(item[key])
            else:
                result.append(item[key])
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
