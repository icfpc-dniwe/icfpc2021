import sys
import shapely.affinity
from shapely.geometry import Polygon
from typing import Tuple

from ..client import Client
from ..types import Solution, Problem
from ..validator import validate_stretching
from ..geometry import vertices_to_lines, lines_to_vertices
from ..placement import fit_figure
from ..discretize import discretize_points
from .edge_folding import dummy_folding_solver
from .brute_folder import iterate_folding
from ..rating import rate


PROBLEMS = 59


def solve_problem(client: Client, problem: Problem) -> Solution:
    folded_vertices = iterate_folding(problem, 1000)
    hole = Polygon(problem.hole)
    figure = vertices_to_lines(folded_vertices, problem.figure.edges)
    moved_figure = fit_figure(hole, figure)
    if moved_figure is None:
        raise RuntimeError("Failed to fit figure into hole")
    fit_vertices = lines_to_vertices(problem.figure.edges, moved_figure)
    discrete_vertices = discretize_points(hole, problem.figure.edges, fit_vertices)
    if discrete_vertices is None:
        raise RuntimeError("Failed to discretize points")
    solution = Solution(vertices=discrete_vertices)
    if not validate_stretching(problem, solution):
        raise RuntimeError("Solution is overstretched")
    return solution


def main():
    with open(sys.argv[1]) as tf:
        token = tf.read().strip()
    client = Client(token)
    for problem_id in range(1, PROBLEMS + 1):
        problem = client.get_problem(problem_id)
        print(f"Solving problem {problem_id}")
        try:
            solution = solve_problem(client, problem)
        except RuntimeError as e:
            print(e)
            continue
        solution_rate = rate(problem, solution)
        print(f"Problem solved, {solution_rate} dislikes")
        client.post_solution(problem_id, solution)


if __name__ == "__main__":
    main()
