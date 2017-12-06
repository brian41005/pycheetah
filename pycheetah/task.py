import logging
from queue import PriorityQueue
from .container import Result
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

    def start(self):
        result = []
        for i, url in enumerate(self.urls):
            newpage = TaskManager.__page_class__(str(i), url)
            newpage.start()
            self.queue.put(newpage)

            if self.queue.full():
                while not self.queue.empty():
                    page = self.queue.get()
                    need_to_break = page.is_alive()
                    temp_result = page.join(timeout=0.5)
                    if temp_result:
                        result.append(temp_result)
                        logging.info(page.url)
                    else:
                        self.queue.put(page)
                        logging.info(page.url + ' [TIMEOUT]')

                    if need_to_break:
                        break

        while not self.queue.empty():
            page = self.queue.get()
            result.append(page.join())
            logging.info(page.url)
        return Result(result)
