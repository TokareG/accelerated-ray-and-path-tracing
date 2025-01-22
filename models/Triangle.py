from typing import List
from core.Utils import *
from core.Ray import *

class Triangle:
    def __init__(self, v0, v1, v2, material = None):
        self.v0, self.v1, self.v2 = v0, v1, v2
        self.normal = cross(sub(v1, v0), sub(v2, v0))
        self.unit_norm = norm(self.normal)
        self.material = material

    def hit(self, ray: Ray):
        # Möller-Trumbore algorithm
        EPSILON = 1e-8
        edge1 = sub(self.v1, self.v0)
        edge2 = sub(self.v2, self.v0)
        h = cross(ray.direction, edge2)
        a = dot(edge1, h)

        if -EPSILON < a < EPSILON:
            return None  # Ray is parallel to the triangle plane

        f = 1.0 / a
        s = sub(ray.origin, self.v0)
        u = f * dot(s, h)

        if u < 0.0 or u > 1.0:
            return None  # Intersection point is outside the triangle

        q = cross(s, edge1)
        v = f * dot(ray.direction, q)

        if v < 0.0 or u + v > 1.0:
            return None  # Intersection point is outside the triangle

        # Compute t to find the intersection point
        t = f * dot(edge2, q)

        if t > EPSILON:
            intersection_point = ray.at(t)
            return t, intersection_point  # t and intersection point
        else:
            return None