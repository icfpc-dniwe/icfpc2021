from shapely.geometry import Polygon, MultiLineString
import shapely.affinity
import scipy.optimize
import math

from .types import *
from .rating import rate_points


def figure_bounds(hole: Polygon, shape: MultiLineString):
    (shape_minx, shape_miny, shape_maxx, shape_maxy) = shape.bounds
    (hole_minx, hole_miny, hole_maxx, hole_maxy) = hole.bounds
    x_dist = hole_minx - shape_minx
    y_dist = hole_miny - shape_miny
    return [
        (0, 2*math.pi),
        (hole_minx - shape_minx, hole_maxx - shape_minx),
        (hole_miny - shape_miny, hole_maxy - shape_miny),
    ]


def fit_figure_function(hole: Polygon, shape: MultiLineString, use_rating=True):
    shape_centroid = shape.centroid

    def f(args):
        rotate = args[0]
        move_x = args[1]
        move_y = args[2]

        candidate = shapely.affinity.rotate(shape, rotate, shape_centroid, use_radians=True)
        candidate = shapely.affinity.translate(candidate, move_x, move_y)

        diff = candidate.difference(hole)
        if diff.length > 0:
            return diff.length
        elif use_rating:
            shape_points = [point for line in candidate.geoms for point in line.coords]
            rate = rate_points(hole.exterior.coords, shape_points)
            return -1 / rate
        else:
            return 0
    return f


def fit_figure(hole: Polygon, shape: MultiLineString, use_rating=True):
    func = fit_figure_function(hole, shape, use_rating=use_rating)
    bounds = figure_bounds(hole, shape)

    if use_rating:
        callback = None
    else:
        def callback(xk, *args):
            return func(xk) <= 0

    res = scipy.optimize.dual_annealing(func, bounds, callback=callback, local_search_options={"method": "Nelder-Mead"})

    if res.fun > 0:
        return None

    candidate = shapely.affinity.rotate(shape, res.x[0], "centroid", use_radians=True)
    candidate = shapely.affinity.translate(candidate, res.x[1], res.x[2])
    return candidate
