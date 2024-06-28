import csv


class JobSlice:
    def __init__(self, identifier, start: int, amount: int):
        self.identifier = identifier
        self.start = start
        self.amount = amount

    def __str__(self):
        return f'Slice("{self.identifier}", start={self.start}, amount={self.amount})'


def save_csv(path: str, jobs: list[JobSlice]):
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['identifier', 'start', 'amount'])
        for job in jobs:
            writer.writerow([job.identifier, job.start, job.amount])