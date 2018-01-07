# coding: utf-8

import itertools
from datetime import datetime, timedelta

__all__ = ['gen_urls', 'partition']


def partition(container, n):
    '''
    container: list like object

    n: int, greater than 0 

    '''
    if n < 1:
        raise ValueError('n must greater than 0')

    len_ = len(container)
    chunk_size = int(len_ / n)
    n -= 1
    chunk = []
    for i in range(n):
        start = chunk_size * i
        chunk.append(container[start:start + chunk_size])

    start = chunk_size * n
    chunk.append(container[start:])
    return chunk


def gen_urls(url, startdate=None, enddate=None, date_format='%Y/%b/%d', product=['date']):
    '''
    general generator for news url

    url: string, like 'https://www.theguardian.com/%s/%s/all'

    startdate: string, like '2007/1/1'

    enddate: string, like '2017/5/31'

    date_format: format, '%Y/%m/%d'

    product: list, Cartesian product ['date'] or ['date', other, other, ...]

    '''
    if startdate and enddate:
        start = datetime.strptime(startdate, '%Y/%m/%d')
        end = datetime.strptime(enddate, '%Y/%m/%d')
        datelist = [(start + timedelta(days=x)).strftime(date_format).lower()
                    for x in range(0, (end - start).days + 1)]
    try:

        date_index = product.index('date')
        product[date_index] = datelist
    except ValueError:
        pass

    product = list(itertools.product(*product))
    for each_prod in product:
        yield url % each_prod
