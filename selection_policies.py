from branch_bound import Node


def min_upper_bound(nodes: list[Node]) -> Node:
    m = min(nodes, key=lambda n: n.upper_bound())
    nodes.remove(m)
    return m


def fifo(nodes: list[Node]) -> Node:
    return nodes.pop(0)


def lifo(nodes: list[Node]) -> Node:
    return nodes.pop()