import math
import functools
from typing import List
from shapely.geometry import Polygon

from .types import *
from .geometry import distance2, vertices_to_lines


def discretize_points(hole: Polygon, edges: List[Edge], points: List[PointF]):
    new_points = list(points)
    buffered_hole = hole.buffer(1e-8)
    for i, (x, y) in enumerate(new_points):
        x_floor = math.floor(x)
        x_ceil = math.ceil(x)
        y_floor = math.floor(y)
        y_ceil = math.ceil(y)
        candidates = [(x_floor, y_floor), (x_ceil, y_floor), (x_floor, y_ceil), (x_ceil, y_ceil)]
        candidates.sort(key=functools.cmp_to_key(distance2))
        found = False
        for cand in candidates:
            new_points[i] = cand
            figure = vertices_to_lines(new_points, edges)
            if buffered_hole.contains(figure):
                found = True
                break
        if not found:
            raise RuntimeError(f"Cannot discretize point {i}")
    return new_points
