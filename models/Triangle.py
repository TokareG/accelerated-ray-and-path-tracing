from typing import List
from core.Utils import *
from core.Ray import *

class Triangle:
    """
    Represents a triangle in 3D space for ray tracing purposes.

    Attributes:
        v0,v1,v2: The three vertices of the triangle.
        normal: The normal vector of the triangle's plane.
        unit_norm: The unit (normalized) normal vector.
        material: The material properties of the triangle.
    """
    def __init__(self, v0, v1, v2, material = None):
        self.v0, self.v1, self.v2 = v0, v1, v2
        self.normal = cross(sub(v1, v0), sub(v2, v0))
        self.unit_norm = norm(self.normal)
        self.material = material

    def hit(self, ray: Ray):
        """
        Determines if a ray intersects with the triangle using the Möller-Trumbore algorithm.
        """
        EPSILON = 1e-8
        edge1 = sub(self.v1, self.v0)
        edge2 = sub(self.v2, self.v0)
        h = cross(ray.direction, edge2)
        a = dot(edge1, h)

        if -EPSILON < a < EPSILON:
            return None

        f = 1.0 / a
        s = sub(ray.origin, self.v0)
        u = f * dot(s, h)

        if u < 0.0 or u > 1.0:
            return None

        q = cross(s, edge1)
        v = f * dot(ray.direction, q)

        if v < 0.0 or u + v > 1.0:
            return None


        t = f * dot(edge2, q)

        if t > EPSILON:
            intersection_point = ray.at(t)
            return t, intersection_point
        else:
            return None