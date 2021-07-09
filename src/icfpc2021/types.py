from dataclasses import dataclass
from typing import List, Tuple

Point = Tuple[float, float]


@dataclass
class Figure:
    edges: List[Point]
    vertices: List[Point]


@dataclass
class Problem:
    hole: List[Point]
    figure: Figure
    epsilon: float
