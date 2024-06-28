import csv


class Job:
    def __init__(self, identifier: str, release_date: int, duration: int):
        self.identifier = identifier
        self.release_date = release_date
        self.duration = duration

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
