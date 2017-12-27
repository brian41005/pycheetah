from enum import Enum

__all__ = ('Command', 'Retry')


class Command(Exception):
    '''Base Command'''


class Retry(Command):
    '''retry this url'''
