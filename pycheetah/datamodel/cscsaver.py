import csv
from abc import ABC


class ISaver(ABC):
    def save(self, file):
        raise NotImplementedError
