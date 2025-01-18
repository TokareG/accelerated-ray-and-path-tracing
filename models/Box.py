import numpy as np
class Box:
    def __init__(self,
                 min_corner: tuple,
                max_corner: tuple,
                 color: tuple,
                 reflection: float,
                 transparency: float,
                 ior: float):
        """
        Initializes the Box object.

        Args:
            min_corner (tuple): The minimum corner of the box (x_min, y_min, z_min).
            max_corner (tuple): The maximum corner of the box (x_max, y_max, z_max).
            color (tuple): The RGB color of the box.
            reflection (float, optional): The reflection coefficient (0..1). Defaults to 0.0.
            transparency (float, optional): The transparency coefficient (0..1). Defaults to 0.0.
            ior (float, optional): The index of refraction. Defaults to 1.0.
        """
        self.min_corner = min_corner
        self.max_corner = max_corner
        self.color = color
        self.reflection = reflection
        self.transparency = transparency
        self.ior = ior

    def intersect(self, ray_origin, ray_dir):
        """
        Calculates the intersection of a ray with the box using the slab method.

        Args:
            ray_origin (tuple): The origin of the ray (x, y, z).
            ray_dir (tuple): The normalized direction vector of the ray.

        Returns:
            float or None: The distance `t` to the intersection point if an intersection occurs,
                           or `None` if there is no intersection.
        """
        t_min = -float('inf')
        t_max = float('inf')

        for i in range(3):
            if abs(ray_dir[i]) < 1e-9:

                if ray_origin[i] < self.min_corner[i] or ray_origin[i] > self.max_corner[i]:
                    return None
            else:
                t1 = (self.min_corner[i] - ray_origin[i]) / ray_dir[i]
                t2 = (self.max_corner[i] - ray_origin[i]) / ray_dir[i]
                tmin_i = min(t1, t2)
                tmax_i = max(t1, t2)
                t_min = max(t_min, tmin_i)
                t_max = min(t_max, tmax_i)

                if t_max < t_min:
                    return None

        if t_min > 0:
            return t_min
        if t_max > 0:
            return t_max
        return None

    def get_normal(self, point):
        """
        Determines the normal vector at a given point on the box's surface.

        Args:
            point (tuple): A point on the surface of the box (x, y, z).

        Returns:
            tuple: The normalized normal vector at the given point (x, y, z).
        """
        eps = 1e-4
        x_min_dist = abs(point[0] - self.min_corner[0])
        x_max_dist = abs(point[0] - self.max_corner[0])
        y_min_dist = abs(point[1] - self.min_corner[1])
        y_max_dist = abs(point[1] - self.max_corner[1])
        z_min_dist = abs(point[2] - self.min_corner[2])
        z_max_dist = abs(point[2] - self.max_corner[2])

        dists = [
            (x_min_dist, np.array([-1, 0, 0], dtype=float)),
            (x_max_dist, np.array([1, 0, 0], dtype=float)),
            (y_min_dist, np.array([0, -1, 0], dtype=float)),
            (y_max_dist, np.array([0, 1, 0], dtype=float)),
            (z_min_dist, np.array([0, 0, -1], dtype=float)),
            (z_max_dist, np.array([0, 0, 1], dtype=float)),
        ]

        dists.sort(key=lambda x: x[0])

        for dist, normal_vec in dists:
            if dist < eps:
                return tuple(normal_vec)
        return (0, 0, 1)