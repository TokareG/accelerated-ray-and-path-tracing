import numpy as np
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
        self.point = np.array(point, dtype=float)
        self.normal = self._normalize(np.array(normal, dtype=float))
        self.color = color
        self.reflection = reflection
        self.transparency = transparency
        self.ior = ior

    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        """
        Normalize a vector.

        Args:
            vector (np.ndarray): The vector to normalize.

        Returns:
            np.ndarray: The normalized vector.

        Raises:
            ValueError: If the vector has zero length.
        """
        norm = np.linalg.norm(vector)
        if norm == 0:
            raise ValueError("Cannot normalize a zero-length vector.")
        return vector / norm

    def intersect(self, ray_origin: tuple, ray_dir: tuple) -> float | None:
        """
        Calculate intersection of a ray with the plane.

        Args:
            ray_origin (tuple): The origin of the ray (x, y, z).
            ray_dir (tuple): The normalized direction vector of the ray.

        Returns:
            float or None: The distance `t` to the intersection point if an intersection occurs, or None if there is no intersection.
        """
        ray_origin = np.array(ray_origin, dtype=float)
        ray_dir = np.array(ray_dir, dtype=float)
        denom = np.dot(self.normal, ray_dir)
        if np.abs(denom) < 1e-9:
            return None  # No intersection, the ray is parallel to the plane
        t = np.dot(self.point - ray_origin, self.normal) / denom
        if t > 0:
            return t
        return None  # The intersection is behind the ray origin

    def get_normal(self, point: tuple) -> np.ndarray:
        """
        Get the normal vector of the plane.

        Args:
            point (tuple): A point on the plane (x, y, z).

        Returns:
            tuple: The normal vector of the plane.
        """
        # The normal is constant across the plane
        return self.normal
