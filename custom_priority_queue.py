'''from queue import PriorityQueue

class CustomPriorityQueue(PriorityQueue):
    def __init__(self):
        super().__init__()
        self.entry_finder = set()

    def put(self, item, *args, **kwargs):
        super().put(item, *args, **kwargs)
        self.entry_finder.add(item)

    def get(self, *args, **kwargs):
        item = super().get(*args, **kwargs)
        try:
            self.entry_finder.remove(item)
        except KeyError:
            pass
        return item

    def __contains__(self, item):
        return item in self.entry_finder'''
from queue import PriorityQueue
import collections

class CustomPriorityQueue(PriorityQueue):
    def __init__(self):
        super().__init__()
        self.entry_finder = collections.Counter()

    def put(self, item, *args, **kwargs):
        super().put(item, *args, **kwargs)
        self.entry_finder[item] += 1

    def get(self, *args, **kwargs):
        item = super().get(*args, **kwargs)
        self.entry_finder[item] -= 1
        if self.entry_finder[item] == 0:
            del self.entry_finder[item]
        return item

    def __contains__(self, item):
        return item in self.entry_finder
    def peek(self):
        return self.queue[0]