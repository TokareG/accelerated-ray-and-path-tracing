from core.helpers import *
class Plane:
    """Class representing plane scene objects."""

    def __init__(self,
                 point: tuple,
                 normal: tuple,
                 color: tuple,
                 reflection: float,
                 transparency: float,
                 ior: float):
        """
        Initialize a plane object.

        Args:
            point (tuple): A point on the plane (x, y, z).
            normal (tuple): The normal vector of the plane (nx, ny, nz).
            color (tuple): The RGB color of the plane.
            reflection (float): The reflection coefficient (0..1).
            transparency (float): The transparency coefficient (0..1).
            ior (float): The index of refraction.
        """
        self.point = point
        self.normal = helpers.normalize(normal)
        self.color = color
        self.reflection = reflection
        self.transparency = transparency
        self.ior = ior


    def intersect(self, ray_origin: tuple, ray_dir: tuple) -> tuple | None:
        """
        Calculate intersection of a ray with the plane.

        Args:
            ray_origin (tuple): The origin of the ray (x, y, z).
            ray_dir (tuple): The normalized direction vector of the ray.

        Returns:
            tuple or None: The distance `t` to the intersection point if an intersection occurs,
                           along with u and v coordinates (unused for planes), or None if no intersection.
        """
        denom = helpers.dot(self.normal, ray_dir)
        if abs(denom) < 1e-9:
            return None  # No intersection, the ray is parallel to the plane
        t_numerator = helpers.dot(helpers.subtract(self.point, ray_origin), self.normal)
        t = t_numerator / denom
        if t > 1e-6:
            return (t, 0, 0)  # t, u, v (u, v niewykorzystywane dla płaszczyzny)
        return None  # The intersection is behind the ray origin

    def get_normal(self, point: tuple) -> tuple:
        """
        Get the normal vector of the plane.

        Args:
            point (tuple): A point on the plane (x, y, z).

        Returns:
            tuple: The normal vector of the plane.
        """
        return self.normal
