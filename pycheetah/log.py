import functools
import logging
import os
import sys
from datetime import datetime

__all__ = ['init_logger', 'addLogger']


def addLogger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as msg:
            logging.exception(
                'there was an exception in {:s}'.format(func.__name__))
    return wrapper


def init_logger(logdir=None, console=True):
    logging.getLogger().setLevel(logging.DEBUG)
    del logging.getLogger().handlers[:]

    formatstring = '[%(asctime)s][%(threadName)s][%(module)s][%(funcName)s] %(levelname)s: %(message)s'
    formatter = logging.Formatter(formatstring)

    if console:

        consoleLogger = logging.StreamHandler(stream=sys.stdout)
        consoleLogger.setLevel(logging.INFO)
        consoleLogger.setFormatter(formatter)
        logging.getLogger().addHandler(consoleLogger)

    if logdir:
        filename = '%s.log' % datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
        logpath = os.path.join(logdir, filename)
        fileLogger = logging.FileHandler(logpath)
        fileLogger.setLevel(logging.INFO)
        fileLogger.setFormatter(formatter)
        logging.getLogger().addHandler(fileLogger)
    logging.info('You got (%s) logging handler' %
                 str(logging.getLogger().handlers))
