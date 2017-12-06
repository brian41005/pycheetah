# coding: utf-8
import logging
import os
import sys
from datetime import datetime, timedelta
import itertools
__all__ = ['gen_urls', 'partition', 'init_logger']


def partition(container, n):
    '''
    container: list like object

    n: int, greater than 0 

    '''
    len_ = len(container)
    chunk_size = int(len_ / n)
    for i in range(n - 1):
        start = chunk_size * i
        yield container[start:start + chunk_size]

    start = chunk_size * n
    yield container[start:]


def gen_urls(url, startdate, enddate, *, date_format='%Y/%b/%d', product=['date']):
    '''general generator for news url

    url: string, like 'https://www.theguardian.com/%s/%s/all'

    startdate: string, like '2007/1/1'

    enddate: string, like '2017/5/31'

    date_format: format, '%Y/%m/%d'

    product: ['date'] or ['date', other, other, ...]

    '''
    start = datetime.strptime(startdate, '%Y/%m/%d')
    end = datetime.strptime(enddate, '%Y/%m/%d')
    datelist = [(start + timedelta(days=x)).strftime(date_format).lower()
                for x in range(0, (end - start).days + 1)]

    date_index = product.index('date')
    product[date_index] = datelist
    product = list(itertools.product(*product))
    for each_prod in product:
        yield url % each_prod


def init_logger(logdir=None, console=True):
    logging.getLogger().setLevel(logging.DEBUG)
    del logging.getLogger().handlers[:]

    #formatstring = '[%(asctime)s][%(threadName)s][%(module)s][%(funcName)s] %(levelname)s: %(message)s'
    formatstring = '[%(asctime)s][%(funcName)s] %(levelname)s: %(message)s'
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
