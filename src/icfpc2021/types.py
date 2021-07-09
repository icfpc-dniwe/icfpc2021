from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Tuple
from shapely.geometry import Polygon, MultiLineString


Point = Tuple[int, int]
PointI = Tuple[int, int]


def figure_lines(vertices: List[Point], edges: List[PointI]):
    lines = [(vertices[ai], vertices[bi]) for (ai, bi) in edges]
    return MultiLineString(lines)


@dataclass_json
@dataclass
class Figure:
    edges: List[Point]
    vertices: List[Point]

    def figure_lines(self):
        return figure_lines(self.vertices, self.edges)


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

    def solution_lines(self, figure: Figure):
        return figure_lines(self.vertices, figure.edges)
