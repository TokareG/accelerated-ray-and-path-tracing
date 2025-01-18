import numpy as np
from core.helpers import *
class Sphere:
    """Class representing sphere scene objects."""
    
    def __init__(self, 
                 center: tuple, 
                 radius: float,
                 color: tuple,
                 reflection: float,
                 transparency: float,
                 ior: float):
        """
        Initialize a sphere object.

        Args:
            center (tuple): The center of the sphere (cx, cy, cz).
            radius (float): The radius of the sphere.
            color (tuple): The RGB color of the sphere.
            reflection (float): The reflection coefficient (0..1).
            transparency (float): The transparency coefficient (0..1).
            ior (float): The index of refraction.
        """
        self.center = center
        self.radius = radius
        self.color = color
        self.reflection = reflection
        self.transparency = transparency
        self.ior = ior

    def intersect(self, ray_origin: tuple, ray_dir: tuple) -> float | None:
        """
        Calculate intersection of a ray with the sphere.

        Args:
            ray_origin (tuple): The origin of the ray (x, y, z).
            ray_dir (tuple): The normalized direction vector of the ray.

        Returns:
            float or None: The distance `t` to the intersection point if an intersection occurs, or None if there is no intersection.
        """
        OC = helpers.subtract(ray_origin, self.center)
        a = helpers.dot(ray_dir, ray_dir)
        b = 2.0 * helpers.dot(OC, ray_dir)
        c = helpers.dot(OC, OC) - self.radius * self.radius
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None
        sqrt_disc = discriminant ** 0.5
        t1 = (-b - sqrt_disc) / (2.0 * a)
        t2 = (-b + sqrt_disc) / (2.0 * a)
        if t1 > 1e-6:
            return t1, 0, 0  # t, u, v (u, v niewykorzystywane dla sfer)
        if t2 > 1e-6:
            return t2, 0, 0
        return None
    
    def get_normal(self, point):
        normal = helpers.subtract(point, self.center)
        return helpers.normalize(normal)
