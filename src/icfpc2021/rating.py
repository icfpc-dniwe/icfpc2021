from .types import *
from .geometry import distance2


def rate(problem: Problem, solution: Solution):
    rate = 0
    for corner in problem.hole:
        rate += min(map(lambda vertex: distance2(corner, vertex), solution.vertices))
    return rate
