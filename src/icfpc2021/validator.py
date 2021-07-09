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


def validate_stretching(problem: Problem, solution: Solution) -> bool:
    original_figure = problem.figure
    for cur_edge in original_figure.edges:
        original_pair = original_figure.vertices[cur_edge[0]], original_figure.vertices[cur_edge[1]]
        moved_pair = solution.vertices[cur_edge[0]], solution.vertices[cur_edge[1]]
        if not check_stretching(original_pair, moved_pair, problem.epsilon):
            return False
    return True


def validate_fitting(problem: Problem, solution: Solution) -> bool:
    return problem.hole_surface().contains(solution.solution_lines(problem.figure))


def validate_solution(problem: Problem, solution: Solution) -> bool:
    valid_stretching = validate_stretching(problem, solution)
    valid_fitting = validate_fitting(problem, solution)
    return valid_stretching and valid_fitting
