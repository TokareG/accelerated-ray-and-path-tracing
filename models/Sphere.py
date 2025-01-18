import numpy as np
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
        OC = ray_origin - self.center
        a = np.dot(ray_dir, ray_dir)
        b = 2.0 * np.dot(OC, ray_dir)
        c = np.dot(OC, OC) - self.radius**2

        disc = b*b - 4*a*c
        if disc < 0:
            return None

        sqrt_disc = np.sqrt(disc)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)

        if t1 > 0 and t2 > 0:
            return min(t1, t2)
        elif t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        return None
    
    def get_normal(self, point):
        """
        Calculate the normal vector at a given point on the surface of the object.

        Args:
            point (tuple): A 3D point (x, y, z) on the surface of the object.

        Returns:
            tuple: A 3D unit vector (x, y, z) representing the normal at the given point.

        Raises:
            ValueError: If the point is identical to the center, causing a division by zero.

        """
        return (point - self.center) / np.linarg.norm(point - self.center)
