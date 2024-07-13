import csv
import itertools
import sys

import benchmark
import branch_bound
import mip
import utils
from generator import HaririPotts, Dummy
from heuristics import aprtf, ect, est, prtf
from selection_policies import fifo, lifo, best_fit
from timeout import Timeout

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
    writer.writerow(['scheme', 'policy', 'use_heuristic', 'job_per_instance', 'gurobi_t', 't', 'gurobi_val', 'val', 'node_count', 'best_heuristic', 'gurobi_timeout', 'timeout'])
    for h in itertools.product(generators.keys(), policies, warm_start, instance_sizes):
        scheme, policy, use_warm_start, n = h
        scheme_name = generators[scheme]
        policy_name = policy.__name__
        for i in range(m):
            jobs = scheme.generate_instances(n)
            gurobi_timeout = False
            gurobi_t = '-'
            try:
                gurobi_sol, gurobi_val, gurobi_t = mip.solve(jobs, integrality_focus=1)
                gurobi_t = str(gurobi_t / int(10e9))
            except Timeout as e:
                gurobi_sol, gurobi_val, gurobi_t = e.inc, e.val, str(e.elapsed / int(10e9))
                gurobi_timeout = True
            name, inc, val = utils.best_heuristic(jobs, heuristics_list) if use_warm_start else 'none', [], sys.maxsize
            info = benchmark.Info(set(jobs), name)
            timeout = False
            t = '-'
            try:
                sol, val = branch_bound.solve(set(jobs), policy, info, warm_start=(inc, val))
                t = str(info.time_ns / int(10e9))
            except Timeout as e:
                sol, val, t = e.inc, e.val, str(e.elapsed / int(10e9))
                timeout = True
            row = [scheme_name, policy_name, str(use_warm_start), str(n), gurobi_t, t, str(gurobi_val), str(val), str(info.node_count), info.heuristic, str(timeout)]
            print(', '.join(row))
            writer.writerow(row)
