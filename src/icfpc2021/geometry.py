from numba import njit
import math
from .types import Point


@njit
def distance2(left_point: Point, right_point: Point) -> float:
    return (left_point[0] - right_point[0]) ** 2 + (left_point[1] - right_point[1]) ** 2


@njit
def distance(left_point: Point, right_point: Point) -> float:
    return math.sqrt(distance2(left_point, right_point))
