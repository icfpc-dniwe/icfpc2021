from numba import njit
import math
from shapely.geometry import Polygon, LineString
from itertools import combinations
from .types import Point
from typing import List, Tuple


@njit
def distance2(left_point: Point, right_point: Point) -> float:
    return (left_point[0] - right_point[0]) ** 2 + (left_point[1] - right_point[1]) ** 2


@njit
def distance(left_point: Point, right_point: Point) -> float:
    return math.sqrt(distance2(left_point, right_point))


def find_longest_diagonal(polygon: Polygon) -> Tuple[Point, Point]:
    points = polygon.coords
    max_length = -1
    max_diag = None
    for left_point, right_point in combinations(points, 2):
        if polygon.buffer(1e-9).contains(LineString((left_point, right_point))):
            cur_length = distance2(left_point, right_point)
            if cur_length > max_length:
                max_length = cur_length
                max_diag = left_point, right_point
    return max_diag


def find_longest_vertical(polygon: Polygon) -> Tuple[Point, Point]:
    pass
