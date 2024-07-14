import csv
import itertools
import sys
from typing import Iterable

import benchmark
import branch_bound
import job
import mip
import utils
from heuristics import aprtf, ect, est, prtf
from node import Node
from node_queue import FifoQueue, LifoQueue, LeastCostQueue
from timeout import Timeout


def fifo(nodes: Iterable[Node]) -> FifoQueue:
    return FifoQueue(nodes)


def lifo(nodes: Iterable[Node]) -> LifoQueue:
    return LifoQueue(nodes)


def least_cost(nodes: Iterable[Node]) -> LeastCostQueue:
    return LeastCostQueue(nodes)


m = 100
sizes = list(range(10, 30, 2))
scheme = ('hariri', 'simple')
heuristics_list = dict([('aprtf', aprtf), ('ect', ect), ('est', est), ('prtf', prtf)])
policies = [fifo, lifo, least_cost]
warm_start = [False, True]
with open('instances/results.csv', 'a+') as f:
    writer = csv.writer(f)
    writer.writerow(
        ['scheme', 'policy', 'use_heuristic', 'job_per_instance', 'gurobi_t', 't', 'gurobi_val', 'val', 'node_count',
         'best_heuristic', 'gurobi_timeout', 'timeout'])
    for g in itertools.product(scheme, sizes, range(m)):
        s, n, i = g
        jobs = job.load_csv(f'instances/{s}/{n}/{i}.csv')
        gurobi_timeout = False
        gurobi_t = '-'
        try:
            gurobi_sol, gurobi_val, gurobi_t = mip.solve(jobs, integrality_focus=1)
            gurobi_t = str(gurobi_t / int(10e9))
        except Timeout as e:
            gurobi_sol, gurobi_val, gurobi_t = e.inc, e.val, str(e.elapsed / int(10e9))
            gurobi_timeout = True
        for h in itertools.product(policies, warm_start):
            policy, use_warm_start = h
            policy_name = policy.__name__
            name, inc, val = utils.best_heuristic(jobs, heuristics_list) if use_warm_start else (
                'none', [], sys.maxsize)
            info = benchmark.Info(set(jobs), name)
            timeout = False
            t = '-'
            try:
                sol, val = branch_bound.solve(set(jobs), policy, info, warm_start=(inc, val))
                t = str(info.time_ns / int(10e9))
            except Timeout as e:
                sol, val, t = e.inc, e.val, str(e.elapsed / int(10e9))
                timeout = True
            row = [s, policy_name, str(use_warm_start), str(n), gurobi_t, t, str(gurobi_val), str(val),
                   str(info.node_count), info.heuristic, str(gurobi_timeout), str(timeout)]
            print(', '.join(row))
            writer.writerow(row)
