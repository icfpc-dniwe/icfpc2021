from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Tuple, Callable, Optional


Point = Tuple[int, int]
Edge = Tuple[int, int]
PointI = Tuple[int, int]
PointF = Tuple[float, float]


@dataclass_json
@dataclass
class Figure:
    edges: List[Edge]
    vertices: List[Point]


@dataclass_json
@dataclass
class Problem:
    hole: List[Point]
    figure: Figure
    epsilon: int


@dataclass_json
@dataclass
class Solution:
    vertices: List[Point]


Solver = Callable[[Problem], Optional[Solution]]
