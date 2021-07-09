from numba import njit
from .types import Point, Problem, Figure
from typing import Optional


@njit
def distance(left_point: Point, right_point: Point) -> float:
    return (left_point[0] - right_point[0]) ** 2 + (left_point[1] - right_point[1]) ** 2


def validate_solution(problem: Problem, figure: Figure) -> Optional[float]:
    return None
