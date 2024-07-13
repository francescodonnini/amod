import csv
import itertools
import sys
from collections import defaultdict

import benchmark
import branch_bound
import mip
import utils
from generator import HaririPotts, Dummy
from heuristics import aprtf, ect, est, prtf
from selection_policies import fifo, lifo, best_fit

g1 = HaririPotts()
g2 = Dummy(duration=(1, 100), release=(0, 10))
m = 100
generators = dict([(g1, 'hariri potts'), (g2, 'simple')])
heuristics_list = dict([('aprtf', aprtf), ('ect', ect), ('est', est), ('prtf', prtf)])
policies = [lifo, fifo, best_fit]
warm_start = [False, True]
instance_sizes = list(range(10, 55, 5))
with open(f'{m}.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['scheme', 'policy', 'use_heuristic', 'job_per_instance', 'gurobi_t', 't', 'gurobi_val', 'val', 'node_count', 'best_heuristic'])
    for h in itertools.product(generators.values(), policies, warm_start, instance_sizes):
        scheme, policy, use_warm_start, n = h
        scheme_name = generators[scheme]
        policy_name = policy.__name__
        for i in range(m):
            jobs = scheme.generate_instances(n)
            gurobi_sol, gurobi_val, gurobi_t = mip.solve(jobs, integrality_focus=1)
            name, inc, val = utils.best_heuristic(jobs, heuristics_list) if use_warm_start else 'none', [], sys.maxsize
            info = benchmark.Info(set(jobs), name)
            sol, val = branch_bound.solve(set(jobs), policy, info, warm_start=(inc, val))
            row = [policy_name, str(use_warm_start), str(n), str(gurobi_t / int(10e9)), str(info.time_ns / int(10e9)), str(gurobi_val), str(val), str(info.node_count), info.heuristic]
            print(', '.join(row))
            writer.writerow([scheme_name, policy_name, str(use_warm_start), str(n), str(gurobi_t / int(10e9)), str(info.time_ns / int(10e9)), str(gurobi_val), str(val), str(info.node_count), info.heuristic])
