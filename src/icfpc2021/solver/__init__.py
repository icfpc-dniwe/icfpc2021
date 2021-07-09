import sys
from ..client import Client
from ..types import Solution
from ..validator import validate_solution
from ..rating import rate


def main():
    with open(sys.argv[1]) as tf:
        token = tf.read().strip()
    client = Client(token)
    # client.hello()
    problem = client.get_problem(1)
    print(problem)
    test_solution = Solution(
        vertices=[
            (21, 28), (31, 28), (31, 87), (29, 41), (44, 43), (58, 70),
            (38, 79), (32, 31), (36, 50), (39, 40), (66, 77), (42, 29),
            (46, 49), (49, 38), (39, 57), (69, 66), (41, 70), (39, 60),
            (42, 25), (40, 35),
        ]
    )
    assert validate_solution(problem, test_solution)
    print(rate(problem, test_solution))
    # client.post_solution(1, test_solution)


if __name__ == "__main__":
    main()
