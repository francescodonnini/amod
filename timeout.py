from slice import JobSlice


class Timeout(Exception):
    def __init__(self, inc: list[JobSlice], val: int, elapsed: int ):
        self.inc = inc
        self.val = val
        self.elapsed = elapsed
