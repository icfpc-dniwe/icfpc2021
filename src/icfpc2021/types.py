from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Tuple

Point = Tuple[int, int]

@dataclass_json
@dataclass
class Figure:
    edges: List[Point]
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
