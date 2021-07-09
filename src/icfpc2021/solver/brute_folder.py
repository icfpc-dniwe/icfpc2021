import numpy as np
from itertools import combinations
from pathos.multiprocessing import ProcessPool
from shapely.geometry import MultiLineString
from ..geometry import mirror_against, vertices_to_lines
from ..validator import validate_stretching
from ..types import PointF, Edge, Problem, Solution
from typing import List, Tuple, Generator, Sequence, Optional


def next_fold(edges: Sequence[Edge], vertices: Sequence[PointF]) -> Generator[Sequence[PointF], None, None]:
    with ProcessPool(6) as p:
        maybe_folded_results = p.map(lambda cur_edge: mirror_against(edges, vertices, cur_edge),
                                     combinations(range(len(vertices)), 2))
    for maybe_folded in maybe_folded_results:
        if maybe_folded is not None:
            yield maybe_folded


def iterate_folding(problem: Problem, max_iterations: int = 10 ** 5) -> Sequence[PointF]:
    cur_iter = -1
    orig_vertices = problem.figure.vertices
    cur_verticies = orig_vertices
    edges = problem.figure.edges
    solution_float = cur_verticies
    hull = vertices_to_lines(cur_verticies, edges).convex_hull
    cur_area = hull.area
    try_find = True
    while try_find:
        try_find = False
        for maybe_folded in next_fold(edges, cur_verticies):
            cur_iter += 1
            if cur_iter >= max_iterations:
                return solution_float
            hull = vertices_to_lines(maybe_folded, edges).convex_hull
            solution = Solution(vertices=[(round(cur_v[0]), round(cur_v[1])) for cur_v in maybe_folded])
            if validate_stretching(problem, solution) and hull.area < cur_area:
                try_find = True
                cur_area = hull.area
                solution_float = maybe_folded
                cur_verticies = maybe_folded
                break
    return solution_float
