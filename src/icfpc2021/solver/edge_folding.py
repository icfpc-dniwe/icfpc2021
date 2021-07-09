import numpy as np
from shapely.geometry import Polygon, LineString
from itertools import combinations
from ..types import Problem, Edge, Solution, Figure, Point
from ..validator import validate_stretching, check_stretching
from ..geometry import distance2
from typing import Optional, Tuple, List


LEFT_POSITION = 0
RIGHT_POSITION = 1


def fold_figure(figure: Figure, start_edge: int = 0) -> Optional[List[int]]:
    moved_vertices = np.zeros(len(figure.vertices), dtype=np.bool_)
    vertices_positions = np.zeros(len(figure.vertices), dtype=np.uint8)
    current_edge = figure.edges[start_edge]
    moved_vertices[current_edge[0]] = True
    moved_vertices[current_edge[1]] = True
    vertices_positions[current_edge[0]] = LEFT_POSITION
    vertices_positions[current_edge[1]] = RIGHT_POSITION
    to_position = LEFT_POSITION

    def get_next_edge() -> Optional[Edge]:
        for maybe_next_edge in figure.edges:
            if maybe_next_edge[0] == current_edge[1] and not moved_vertices[maybe_next_edge[1]]:
                return maybe_next_edge
            if maybe_next_edge[1] == current_edge[1] and not moved_vertices[maybe_next_edge[0]]:
                return maybe_next_edge[1], maybe_next_edge[0]
        return None

    while not np.alltrue(moved_vertices):
        next_edge = get_next_edge()
        if next_edge is None:
            return None
        moved_vertices[next_edge[1]] = True
        vertices_positions[next_edge[1]] = to_position
        to_position = LEFT_POSITION if to_position == RIGHT_POSITION else RIGHT_POSITION
        current_edge = next_edge
    return vertices_positions.tolist()


def _make_solution(left_position: Point, right_position: Point, verticies_positions: List[int]) -> Solution:
    positions = left_position, right_position
    return Solution(vertices=[positions[cur_pos] for cur_pos in verticies_positions])


def fit_line_inside_polygon(line: Tuple[Point, Point], polygon: List[Point]) -> Optional[Tuple[Point, Point]]:
    solution_length = distance2(*line)
    found_line = None
    found_length = None
    hole = Polygon(polygon)
    for left_point, right_point in combinations(polygon, 2):
        cur_length = distance2(left_point, right_point)
        if cur_length >= solution_length and hole.contains(LineString((left_point, right_point))):
            found_line = left_point, right_point
            found_length = cur_length
            break
    if found_line is None:
        return None
    solution_left = found_line[0]
    coeff = np.sqrt(solution_length / found_length)
    solution_right = (round(coeff * (found_line[1][0] - found_line[0][0])) + solution_left[0],
                      round(coeff * (found_line[1][1] - found_line[0][1])) + solution_left[1])
    return solution_left, solution_right


def dummy_folding_solver(problem: Problem) -> Optional[Solution]:
    solution = None
    solution_edge = None
    edges = problem.figure.edges
    vertices = problem.figure.vertices
    # find folding solution
    for start_edge in range(len(edges)):
        maybe_solution = fold_figure(problem.figure, start_edge)
        if maybe_solution is None:
            continue
        left_position = vertices[edges[start_edge][0]]
        right_position = vertices[edges[start_edge][1]]
        if validate_stretching(problem, _make_solution(left_position, right_position, maybe_solution)):
            solution = maybe_solution
            solution_edge = start_edge
            break
    if solution is None:
        print('Could not fold')
        return None
    print('Folded:', solution)
    # fit solution inside the hole
    edge = problem.figure.edges[solution_edge]
    vertices = problem.figure.vertices
    positions = fit_line_inside_polygon((vertices[edge[0]], vertices[edge[1]]), problem.hole)
    if positions is None:
        return None
    for shift_x in (-1, 0, 1):
        for shift_y in (-1, 0, 1):
            right_pos = positions[1][0] + shift_x, positions[1][1] + shift_y
            if check_stretching((vertices[edge[0]], vertices[edge[1]]),
                                (positions[0], tuple(right_pos)),
                                problem.epsilon):
                positions = positions[0], right_pos
                break
    return _make_solution(positions[0], positions[1], solution)
