from typing import List

from .types import *
from .geometry import distance2


def rate_points(hole: List[PointF], points: List[PointF]):
    rate = 0
    for corner in hole:
        rate += min(map(lambda vertex: distance2(corner, vertex), points))
    return rate


def rate(problem: Problem, solution: Solution):
    return rate_points(problem.hole, solution.vertices)
