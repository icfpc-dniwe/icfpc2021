import sys
from ..client import Client
from ..types import Solution, Problem
from ..validator import validate_solution
from .edge_folding import dummy_folding_solver
from ..rating import rate
from typing import Tuple


def solve_problem(client: Client, problem_id: int) -> Tuple[Problem, Solution]:
    problem = client.get_problem(problem_id)
    # print(problem)
    test_solution = Solution(
        vertices=[
            (20, 0), (40, 20), (20, 40), (0, 20)
        ]
    )
    solution = None  # dummy_folding_solver(problem)
    # print('Solution:', solution)
    if solution is None:
        solution = test_solution  # Solution(vertices=problem.figure.vertices)
    return problem, solution


def main():
    with open(sys.argv[1]) as tf:
        token = tf.read().strip()
    client = Client(token)
    # client.hello()
    for problem_id in range(13, 14):
        problem, solution = solve_problem(client, problem_id)
        if validate_solution(problem, solution):
            print('Solved!', problem_id, rate(problem, solution))
        client.post_solution(problem_id, solution)
    # assert validate_solution(problem, solution)
    # print(rate(problem, solution))
    # client.post_solution(1, test_solution)


if __name__ == "__main__":
    main()
