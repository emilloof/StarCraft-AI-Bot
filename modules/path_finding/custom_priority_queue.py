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
        try:
            self.entry_finder.remove(item)
        except KeyError:
            print("KeyError")
            pass
        print("get", item)
        return item

    def __contains__(self, item):
        return item in self.entry_finder
    
    
'''from queue import PriorityQueue
removed = (0.5050505, 0.5050505)
class CustomPriorityQueue(PriorityQueue):
    def __init__(self):
        super().__init__()
        self.entry_finder = {}

    def put(self, item, *args, **kwargs):
        priority, vertex = item
        self.entry_finder[vertex] = item
        super().put(item, *args, **kwargs)

    def get(self, *args, **kwargs):
        while not self.empty():
            item = super().get(self, *args, **kwargs)
            if item[-1] != removed:
                return item
        raise Exception("Queue is empty")

        
        while True:
            item = super().get()
            priority, vertex = item
            ic(item)
            ic(self.entry_finder)
            if item is not self.queue[0]:
                if vertex != 'REMOVED':
                    if vertex in self.entry_finder:
                        del self.entry_finder[vertex]
                    return item

    
    def remove(self, item):
        entry = self.entry_finder[item[1]]
        ic(entry) # remove vertex
        entry = (entry[0], removed)

    def __contains__(self, item):
        return item in self.entry_finder and self.entry_finder[item][-1] != removed
    
    def update(self, item: tuple["key", "vertex"]):
        if item in self.entry_finder:
            self.remove(item)
        self.put(item)
    
    def peek(self):
        if self.empty():
            return None
        return self.queue[0]'''
