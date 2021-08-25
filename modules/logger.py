import time
from typing import Any


class Logger:
    """Saves logging information"""

    def __init__(self):
        self.keys = []
        self.logs = []
        self._current_item = {}

    def new_row(self) -> None:
        """Adds new empty row"""
        if self._current_item:
            self.logs.append(self._current_item)
            self._current_item = {}

    def add(self, key: str, value: Any) -> None:
        """Adds new value to key on current row"""
        if key not in self.keys:
            self.keys.append(key)
        self._current_item[key] = value

    def save(self) -> None:
        """Saves log to file"""
        with open(f"logs/log-{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}.csv", "w") as f:
            f.write(", ".join([str(key) for key in self.keys]) + "\n")
            for elem in self.logs:
                data = [str(elem[key] if key in elem else 0) for key in self.keys]
                f.write(", ".join(data) + "\n")
