from numba import njit
from shapely.geometry import LineString, MultiLineString
from shapely.geometry.polygon import Polygon
from typing import Tuple

from .types import Point, Problem, Figure, Solution
from .geometry import distance2


@njit
def check_stretching(origin_pair: Tuple[Point, Point], moved_pair: Tuple[Point, Point], eps: int) -> bool:
    return abs(distance2(*moved_pair) / distance2(*origin_pair) - 1) < (eps / 10 ** 6)


def check_edge(hole: Polygon, edge: Tuple[Point, Point]) -> bool:
    return hole.contains(LineString(edge))


def validate_solution(problem: Problem, solution: Solution) -> bool:
    # check stretching
    original_figure = problem.figure
    for cur_edge in original_figure.edges:
        original_pair = original_figure.vertices[cur_edge[0]], original_figure.vertices[cur_edge[1]]
        moved_pair = solution.vertices[cur_edge[0]], solution.vertices[cur_edge[1]]
        if not check_stretching(original_pair, moved_pair, problem.epsilon):
            return False
    # check fitting inside the hole
    return problem.hole_surface().contains(solution.solution_lines(problem.figure))
