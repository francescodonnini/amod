import csv


class Job:
    def __init__(self, identifier: str, release_date: int, duration: int):
        self.identifier = identifier
        self.release_date = release_date
        self.duration = duration

    def __hash__(self) -> int:
        return hash((self.identifier, self.release_date, self.duration))

    def __eq__(self, other: 'Job') -> bool:
        return self.identifier == other.identifier and self.release_date == other.release_date and self.duration == other.duration

    def __str__(self):
        return f'Job("{self.identifier}", release={self.release_date}, duration={self.duration})'


def load_csv(file: str) -> list[Job]:
    jobs = []
    with open(file, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for job in reader:
            job: dict
            jobs.append(Job(job['job'], int(job['release']), int(job['duration'])))
    return jobs


def save_csv(jobs: list[Job], path: str):
    with open(path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['job', 'release', 'duration'])
        for j in jobs:
            writer.writerow([j.identifier, j.release_date, j.duration])

