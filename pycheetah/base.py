from . import log

__all__ = ['BaseCheetah']


class BaseCheetah:
    __workers__ = {}
    __request__ = None

    def __new__(cls, *args, **kwargs):
        if not (BaseCheetah.__workers__ and BaseCheetah.__request__):
            for func_str in (set(dir(cls)) - set(dir(BaseCheetah))):
                func = getattr(cls, func_str)
                if func.__name__.startswith('get_') and callable(func):
                    name = func.__name__.replace('get_', '')
                    BaseCheetah.__workers__[name] = log.addLogger(func)
                elif func.__name__ == 'request' and callable(func):
                    BaseCheetah.__request__ = log.addLogger(func)

            if not BaseCheetah.__request__ and \
                    not callable(BaseCheetah.__request__):
                raise NotImplementedError('request method not found!')

        return super(BaseCheetah, cls).__new__(cls)

    def run(self):
        pass

    def __call__(self):
        return self.run()

    def start(self):
        return self.run()
