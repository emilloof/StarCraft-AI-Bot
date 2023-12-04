from queue import PriorityQueue

class CustomPriorityQueue(PriorityQueue):
    def __init__(self):
        super().__init__()
        self.entry_finder = set()

    def put(self, item, *args, **kwargs):
        super().put(item, *args, **kwargs)
        self.entry_finder.add(item)

    def get(self, *args, **kwargs):
        item = super().get(*args, **kwargs)
        self.entry_finder.remove(item)
        return item

    def __contains__(self, item):
        return item in self.entry_finder