import logging
import threading
from heapq import heappop, heappush
from queue import Empty, Full, PriorityQueue, Queue

__all__ = ['TaskManager']


class TaskManager:
    __page_class__ = None

    def __new__(cls, *args, **kwargs):
        TaskManager.__page_class__ = cls.__page_class__
        return super(TaskManager, cls).__new__(cls)

    def __init__(self, urls, num_thread=1):
        self.queue = PriorityQueue(maxsize=num_thread)
        self.urls = urls
        self.num_thread = num_thread
        self.result = []

    def start(self):
        for i, url in enumerate(self.urls):
            newpage = TaskManager.__page_class__(str(i), url)
            newpage.start()
            self.queue.put(newpage)

            if self.queue.full():
                while not self.queue.empty():
                    page = self.queue.get()
                    need_to_break = page.is_alive()
                    self.result.append(page.join())
                    logging.info(page.url)
                    if need_to_break:
                        break

        while not self.queue.empty():
            page = self.queue.get()
            self.result.append(page.join())
            logging.info(page.url)
