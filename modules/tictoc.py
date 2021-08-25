import time


class TicToc:
    """
    Class for tracking the time it takes for code snippets to execute, inspired by the tic and toc functions in MATLAB.

    This class can store multiple timers with unique keys.

    The timers work additively, meaning that multiple calls to tic and toc on the same key will add the recorded times
    together, so that you can track the total time of a function run multiple times for instance.
    """

    def __init__(self, prints=True):
        self.logs = None
        self._time_start = {"main": 0.0}
        self._await_toc = set()
        self._prints = prints
        if self._prints:
            self._had_toc = set()
        self.reset()

    def __repr__(self):
        return self.logs.__repr__()

    def __getitem__(self, item):
        return self.logs.get(item)

    def __iter__(self):
        return self.logs.items().__iter__()

    def tic(self, key: str = "main") -> None:
        """Starts a timer for the specified key"""
        if key in self._await_toc:
            raise Exception("tic called again before toc, please make sure to follow up every tic with a toc.")

        if key not in self.logs:
            self.logs[key] = 0.0
        self._time_start[key] = time.time()
        self._await_toc.add(key)

    def toc(self, key: str = "main") -> None:
        """Stops the timer for the specified key"""
        if key not in self._await_toc:
            raise Exception("toc called before tic, please make sure to precede every toc with a tic.")

        inc = time.time() - self._time_start[key]
        self.logs[key] += inc
        self._await_toc.remove(key)

        if self._prints:
            inc_str = f" (+{inc})" if key in self._had_toc else ""
            print(f"Toc {key}: {self.logs[key]}{inc_str}")
            self._had_toc.add(key)

    def reset(self) -> None:
        """Resets all timers"""
        self.logs = {"main": 0.0}

        if self._prints:
            print("---Tic---")
            self._had_toc = set()
