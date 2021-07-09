from numba import njit
import math
from queue import Queue
from shapely.geometry import Polygon, LineString
from itertools import combinations
from typing import List, Tuple, Generator, Optional
from shapely.geometry import Polygon, MultiLineString

from .types import *


@njit
def distance2(left_point: PointF, right_point: PointF) -> float:
    return (left_point[0] - right_point[0]) ** 2 + (left_point[1] - right_point[1]) ** 2


@njit
def distance(left_point: PointF, right_point: PointF) -> float:
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


def find_movable_points(figure: Figure, movable_point: int, fixed_points: List[int]) -> List[int]:
    def find_neighbors(point: int) -> Generator[int, None, None]:
        for cur_edge in figure.edges:
            if cur_edge[0] == point:
                yield cur_edge[1]
            elif cur_edge[1] == point:
                yield cur_edge[0]

    watched_points = [False] * len(figure.vertices)
    watched_points[movable_point] = True
    for cur_point in fixed_points:
        watched_points[cur_point] = True
    result = [movable_point]
    points_queue = Queue()
    points_queue.put(movable_point)
    while not points_queue.empty():
        cur_point = points_queue.get()
        for cur_neighbor in find_neighbors(cur_point):
            if not watched_points[cur_neighbor]:
                watched_points[cur_neighbor] = True
                points_queue.put(cur_neighbor)
                result.append(cur_neighbor)
    return result


def vertices_to_lines(vertices: List[Point], edges: List[Edge]) -> MultiLineString:
    lines = [(vertices[ai], vertices[bi]) for (ai, bi) in edges]
    return MultiLineString(lines)


def lines_to_vertices(edges: List[Edge], figure: MultiLineString, vertices_len: Optional[int] = None) -> List[PointF]:
    if vertices_len is None:
        vertices_len = max(map(lambda edge: max(*edge), edges)) + 1
    new_vertices = [(0.0, 0.0)] * vertices_len
    for ((ai, bi), line) in zip(edges, figure.geoms):
        new_vertices[ai] = line.coords[0]
        new_vertices[bi] = line.coords[1]
    return new_vertices


def validate_fitting(problem: Problem, solution: Solution) -> bool:
    return Polygon(problem.hole).buffer(1e-8).contains(vertices_to_lines(solution.vertices, problem.figure.edges))
