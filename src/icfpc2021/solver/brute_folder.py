import numpy as np
from itertools import combinations
from ..geometry import mirror_against
from ..validator import validate_stretching
from ..types import PointF, Edge, Problem, Solution
from typing import List, Tuple, Generator, Sequence, Optional


def next_fold(edges: Sequence[Edge], vertices: Sequence[PointF]) -> Generator[Sequence[PointF], None, None]:
    for cur_edge in combinations(range(len(vertices)), 2):
        maybe_folded = mirror_against(edges, vertices, cur_edge)
        if maybe_folded is None:
            continue
        yield maybe_folded


def iterate_folding(problem: Problem, max_iterations: int = 10 ** 5) -> Optional[Sequence[PointF]]:
    cur_iter = -1
    orig_vertices = np.array(problem.figure.vertices, dtype=np.float32)
    cur_verticies = orig_vertices.copy()
    edges = problem.figure.edges
    solution_float = cur_verticies
    try_find = True
    while try_find:
        try_find = False
        for maybe_folded in next_fold(edges, cur_verticies):
            cur_iter += 1
            if cur_iter >= max_iterations:
                return None
            solution = Solution(vertices=[(round(cur_v[0]), round(cur_v[1])) for cur_v in maybe_folded])
            if validate_stretching(problem, solution):
                try_find = True
                solution_float = maybe_folded
                cur_verticies = np.array(maybe_folded, dtype=np.float32)
                break
    return solution_float
