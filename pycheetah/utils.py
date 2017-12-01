# coding: utf-8
import calendar
from datetime import datetime, timedelta


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


def gen_urls(startdate, enddate, category):
    '''
    startdate: string, like '2007/1/1'

    enddate: string, like '2017/5/31'

    category: list with string elements
    '''
    start = datetime.strptime(startdate, '%Y/%m/%d')
    end = datetime.strptime(enddate, '%Y/%m/%d')
    datelist = [(start + timedelta(days=x)).strftime('%Y/%b/%d').lower()
                for x in range(0, (end - start).days + 1)]
    for d in datelist:
        for c in category:
            yield 'https://www.theguardian.com/%s/%s/all' % (c, d)
