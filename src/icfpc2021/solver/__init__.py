import sys
import shapely.affinity
from shapely.geometry import Polygon
from typing import Tuple

from ..client import Client
from ..types import Solution, Problem
from ..validator import validate_solution
from ..geometry import vertices_to_lines, lines_to_vertices
from ..placement import fit_figure
from ..discretize import discretize_points
from .edge_folding import dummy_folding_solver
from .brute_folder import iterate_folding
from ..rating import rate


def solve_problem(client: Client, problem_id: int) -> Tuple[Problem, Solution]:
    problem = client.get_problem(problem_id)
    # print(problem)
    test_solution = Solution(
        vertices=[
            (20, 0), (40, 20), (0, 20), (20, 40)
        ]
    )
    solution = dummy_folding_solver(problem)
    # print('Solution:', solution)
    if solution is None:
        solution = Solution(vertices=problem.figure.vertices)
    return problem, solution


def solve_first_problem(client: Client):
    problem = client.get_problem(1)
    test_solution = Solution(
        vertices=[
            (21, 28), (31, 28), (31, 87), (29, 41), (44, 43), (58, 70),
            (38, 79), (32, 31), (36, 50), (39, 40), (66, 77), (42, 29),
            (46, 49), (49, 38), (39, 57), (69, 66), (41, 70), (39, 60),
            (42, 25), (40, 35),
        ]
    )
    hole = Polygon(problem.hole)
    original_figure = vertices_to_lines(test_solution.vertices, problem.figure.edges)
    test_figure = shapely.affinity.rotate(original_figure, 15, "centroid", use_radians=True)
    candidate = fit_figure(hole, test_figure)
    test_points = lines_to_vertices(problem.figure.edges, candidate)
    discretized_points = discretize_points(hole, problem.figure.edges, test_points)
    assert validate_solution(problem, Solution(vertices=discretized_points))


def fold_first_problem(client: Client):
    problem = client.get_problem(1)
    folded_solution = iterate_folding(problem, 1000)
    hole = Polygon(problem.hole)
    print(folded_solution)
    # discretized_points = discretize_points(hole, problem.figure.edges, folded_solution)
    # print(validate_solution(problem, Solution(vertices=discretized_points)))


def solve_problem_28():
    for problem_id in range(27, 28):
        print(problem_id, ':')
        problem, solution = solve_problem(client, problem_id)
        if validate_solution(problem, solution):
            print('Solved!', problem_id, rate(problem, solution))


def main():
    with open(sys.argv[1]) as tf:
        token = tf.read().strip()
    client = Client(token)
    fold_first_problem(client)
    # assert validate_solution(problem, solution)
    # print(rate(problem, solution))
    # client.post_solution(1, test_solution)


if __name__ == "__main__":
    main()
