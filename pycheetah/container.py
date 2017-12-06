# coding: utf-8

__all__ = ['Result']


class Result:
    def __init__(self, result=None):
        self.result = result if result else []

    def __repr__(self):
        return self.result.__repr__()

    def __getitem__(self, key):
        if type(key) is str:
            all_ = []
            for i in self.result:
                if key in i:
                    if i[key] is not None:
                        all_.extend(i[key])
            return all_
        elif type(key) is int:
            return self.result[key]

    def __len__(self):
        return len(self.result)

    def extend(self, other):
        if type(other) is Result:
            self.result.extend(other.result)
        else:
            raise TypeError('need  Result')
