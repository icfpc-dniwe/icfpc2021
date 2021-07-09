from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Tuple
from shapely.geometry import Polygon, MultiLineString

Point = Tuple[int, int]

@dataclass_json
@dataclass
class Figure:
    edges: List[Point]
    vertices: List[Point]

    def figure_lines(self):
        lines = [(self.vertices[ai], self.vertices[bi]) for (ai, bi) in self.edges]
        return MultiLineString(lines)

@dataclass_json
@dataclass
class Problem:
    hole: List[Point]
    figure: Figure
    epsilon: int

    def hole_surface(self):
        return Polygon(self.hole)

@dataclass_json
@dataclass
class Solution:
    vertices: List[Point]
