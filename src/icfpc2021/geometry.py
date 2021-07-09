from numba import njit
import numpy as np
import math
from queue import Queue
from shapely.geometry import Polygon, LineString
from itertools import combinations
from typing import List, Tuple, Generator, Sequence
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


def find_neighbors(edges: Sequence[Edge], point: int) -> Generator[int, None, None]:
    for cur_edge in edges:
        if cur_edge[0] == point:
            yield cur_edge[1]
        elif cur_edge[1] == point:
            yield cur_edge[0]


def find_movable_points(edges: Sequence[Edge],
                        vertices: Sequence[PointF],
                        movable_point: int,
                        fixed_points: Sequence[int]
                        ) -> List[int]:
    watched_points = [False] * len(vertices)
    watched_points[movable_point] = True
    for cur_point in fixed_points:
        watched_points[cur_point] = True
    result = [movable_point]
    points_queue = Queue()
    for cur_p in fixed_points:
        points_queue.put(cur_p)
    while not points_queue.empty():
        cur_point = points_queue.get()
        for cur_neighbor in find_neighbors(edges, cur_point):
            if not watched_points[cur_neighbor]:
                watched_points[cur_neighbor] = True
                points_queue.put(cur_neighbor)
    for cur_p, cur_r in enumerate(watched_points):
        if not cur_r:
            result.append([cur_p])
    return result


def find_free_point(edges: Sequence[Edge], fixed_edge: Tuple[int, int]) -> int:
    free_point = None
    for cur_point in find_neighbors(edges, fixed_edge[0]):
        if cur_point != fixed_edge[1]:
            free_point = cur_point
            break
    if free_point is None:
        for cur_point in find_neighbors(edges, fixed_edge[1]):
            if cur_point != fixed_edge[0]:
                free_point = cur_point
                break
    return free_point


@njit
def point_dot(left_point: PointF, right_point: PointF) -> float:
    return left_point[0] * right_point[0] + left_point[1] * right_point[1]


@njit
def mirror_shift(edge: Tuple[PointF, PointF], point: PointF) -> PointF:
    section = np.array(edge[1]) - np.array(edge[0])
    upper = np.array(point) - np.array(edge[0])
    shift = 2 * (np.dot(upper, section) / np.dot(section, section) * section - upper)
    return shift[0], shift[1]


@njit
def shift_points(vertices: Sequence[PointF], shift: PointF) -> List[PointF]:
    return [(cur_v[0] + shift[0], cur_v[1] + shift[1]) for cur_v in vertices]


@njit
def shift_points_filter(vertices: Sequence[PointF], shift: PointF, mask: Sequence[bool]):
    return [(cur_v[0] + shift[0], cur_v[1] + shift[1]) if cur_m else cur_v
            for cur_v, cur_m in zip(vertices, mask)]


def mirror_against(edges: Sequence[Edge],
                   vertices: Sequence[PointF],
                   fixed_edge: Tuple[int, int]
                   ) -> Optional[List[PointF]]:
    free_point = find_free_point(edges, fixed_edge)
    fixed_points = fixed_edge[0], fixed_edge[1]
    movable_points = find_movable_points(edges, vertices, free_point, fixed_points)
    if len(movable_points) + 2 >= len(vertices):
        return None
    shift = mirror_shift((vertices[fixed_edge[0]], vertices[fixed_edge[1]]), vertices[free_point])
    mask = [False] * len(vertices)
    for cur_p in movable_points:
        mask[cur_p] = True
    return shift_points_filter(vertices, shift, mask)


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
