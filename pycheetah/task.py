from concurrent import futures
import logging
from abc import ABC, ABCMeta, abstractmethod
from queue import PriorityQueue

from .container import Result

__all__ = ['DefaultTaskManager']


class ABCTaskManager(metaclass=ABCMeta):
    @abstractmethod
    def start(self):
        pass


class DefaultTaskManager(ABCTaskManager):
    def __init__(self, urls, cheetah, num_thread=1):
        self.urls = urls
        self.cheetah = cheetah
        self.num_thread = min(len(self.urls), num_thread)

    def start(self):
        with futures.ThreadPoolExecutor(self.num_thread) as executor:
            to_do = [executor.submit(self.cheetah('', url))
                     for url in self.urls]
            result = [future.result()
                      for future in futures.as_completed(to_do)]
        return Result(result)


# class OldTaskManager(ABCTaskManager):

#     def __init__(self, urls, cheetah, num_thread=1):
#         self.urls = urls
#         self.num_thread = min(len(self.urls), num_thread)
#         self.queue = PriorityQueue(maxsize=self.num_thread)
#         self.cheetah = cheetah

#     def start(self):
#         result = []
#         for i, url in enumerate(self.urls):
#             newpage = self.cheetah(str(i), url)
#             newpage.start()
#             self.queue.put(newpage)

#             if self.queue.full():
#                 while not self.queue.empty():
#                     page = self.queue.get()
#                     need_to_break = page.is_alive()
#                     temp_result = page.join(timeout=0.5)
#                     if temp_result:
#                         result.append(temp_result)
#                         logging.info(page.url)
#                     else:
#                         self.queue.put(page)
#                         logging.info(page.url + ' [TIMEOUT]')

#                     if need_to_break:
#                         break

#         while not self.queue.empty():
#             page = self.queue.get()
#             result.append(page.join())
#             logging.info(page.url)
#         return Result(result)
