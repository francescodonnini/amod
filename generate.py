import os

import job
from generator import Dummy, HaririPotts

g1 = Dummy(duration=(1, 100), release=(0, 10))
g2 = HaririPotts()
m = 100
sizes = list(range(10, 30, 2))
for n in sizes:
    os.makedirs(f'instances/hariri/{n}')
    os.makedirs(f'instances/simple/{n}')
    for i in range(m):
        j1 = g1.generate_instances(n)
        j2 = g2.generate_instances(n)
        job.save_csv(j1, f'instances/hariri/{n}/{i}.csv')
        job.save_csv(j2, f'instances/simple/{n}/{i}.csv')
