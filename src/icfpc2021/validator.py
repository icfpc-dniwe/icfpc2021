from numba import njit
from shapely.geometry import LineString, MultiLineString
from shapely.geometry.polygon import Polygon
from typing import Tuple

from .types import Point, Problem, Figure, Solution
from .geometry import distance2, vertices_to_lines


@njit
def check_stretching(origin_pair: Tuple[Point, Point], moved_pair: Tuple[Point, Point], eps: int) -> bool:
    dist_fitted = distance2(*moved_pair)
    dist_orig = distance2(*origin_pair)
    stretching_error = abs(dist_fitted / dist_orig - 1)
    result = stretching_error <= (eps / 10 ** 6)
    return result


def check_edge(hole: Polygon, edge: Tuple[Point, Point]) -> bool:
    return hole.buffer(1e-9).contains(LineString(edge))


def validate_stretching(problem: Problem, solution: Solution) -> bool:
    original_figure = problem.figure
    for cur_edge in original_figure.edges:
        original_pair = original_figure.vertices[cur_edge[0]], original_figure.vertices[cur_edge[1]]
        moved_pair = solution.vertices[cur_edge[0]], solution.vertices[cur_edge[1]]
        if not check_stretching(original_pair, moved_pair, problem.epsilon):
            return False
    return True


def validate_fitting(problem: Problem, solution: Solution) -> bool:
    return Polygon(problem.hole).buffer(1e-8).contains(vertices_to_lines(solution.vertices, problem.figure.edges))


def validate_solution(problem: Problem, solution: Solution) -> bool:
    valid_stretching = validate_stretching(problem, solution)
    valid_fitting = validate_fitting(problem, solution)
    return valid_stretching and valid_fitting
