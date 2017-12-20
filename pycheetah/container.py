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
        for i in self:
            if type(i[key]) is list:
                result.extend(i[key])
            else:
                result.append(i[key])
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
