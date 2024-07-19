from job import Job


class Info:
    def __init__(self, heuristic: str):
        self.heuristic = heuristic
        self.node_count = 0
        self.time_ns = 0

    def __str__(self):
        s = f'heuristic={self.heuristic}\n'
        s += f'node_count={self.node_count}\n'
        return s + f'time={self.time_ns / int(1e9)} s'

    def add_node_count(self, c: int):
        if c < 0:
            raise ValueError('non negative value expected')
        self.node_count += c

    def get_node_count(self) -> int:
        return self.node_count

    def get_time(self) -> int:
        return self.time_ns

    def set_time(self, time_ns: int):
        if time_ns < 0:
            raise ValueError('non negative value expected')
        self.time_ns = time_ns
