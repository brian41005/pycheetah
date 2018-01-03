from enum import Enum

__all__ = ['Command', 'Retry', 'Fail']


class Command(Exception):
    '''Base Command'''


class Retry(Command):
    '''retry this url'''


class Fail(Command):
    ''' set aside this url'''
