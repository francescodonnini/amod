from functools import total_ordering

from job import Job


@total_ordering
class RptJob(Job):
    def __init__(self, identifier, release, duration):
        super(RptJob, self).__init__(identifier, release, duration)
        self.rpt = duration

    def __lt__(self, other: 'RptJob') -> bool:
        return self.rpt < other.rpt

    def __str__(self):
        return f'RptJob("{self.identifier}", release={self.release_date}, rpt={self.rpt})'

    def is_completed(self) -> bool:
        return self.rpt == 0

    def expected_rpt(self, amount: int) -> int:
        self.check_amount(amount)
        return self.rpt - amount

    def work(self, amount: int):
        self.check_amount(amount)
        self.rpt -= amount

    def check_amount(self, amount: int):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.rpt:
            raise ValueError("Amount must be less than remaining processing time")
