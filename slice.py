import csv

from job import Job


class JobSlice:
    def __init__(self, job: Job, start: int, amount: int):
        self.job = job
        self.start = start
        self.amount = amount

    def __eq__(self, other: 'JobSlice'):
        return self.job == other.job and self.start == other.start and self.amount == other.amount

    def __hash__(self):
        return hash((self.job, self.start, self.amount))

    def __str__(self):
        return f'Slice("{self.job.identifier}", start={self.start}, amount={self.amount})'


def load_csv(path: str, jobs: list[Job]) -> list[JobSlice]:
    schedule: list[JobSlice] = []
    with open(path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for s in reader:
            s: dict
            j: Job = next(filter(lambda x: find_by_id(x, s['job']), jobs))
            schedule.append(JobSlice(j, int(s['start']), int(s['amount'])))
    return schedule


def find_by_id(job: Job, ident: str) -> bool:
    return job.identifier == ident


def save_csv(path: str, schedule: list[JobSlice]):
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['job', 'start', 'amount'])
        for s in schedule:
            writer.writerow([s.job.identifier, s.start, s.amount])