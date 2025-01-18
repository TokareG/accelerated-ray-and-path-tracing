import numpy as np
from core.helpers import *
class Scene:
    """
    Class that stores objects, light parameters, background, and the trace_ray method.
    """
    def __init__(self, light_pos, background_color, ambient, max_depth):
        self.objects = []
        self.light_pos = tuple(light_pos)
        self.background_color = tuple(background_color)
        self.ambient = ambient
        self.max_depth = max_depth

    def add_object(self, obj):
        """
        Adds an object to the scene.
        """
        self.objects.append(obj)

    def trace_ray(self, ray_origin, ray_dir, depth=0):
        """
        Returns color [R, G, B] (as numpy.array float).
        Supports simple: ambient + diffuse + reflect (reflection).
        (No shadows, no refraction, etc. - to be expanded).
        """
        if depth > self.max_depth:
            return self.background_color

        closest_t = float('inf')
        closest_obj = None
        #bary_u = 0
        #bary_v = 0

        # 1) Znajdź najbliższe przecięcie
        for obj in self.objects:
            hit = obj.intersect(ray_origin, ray_dir)
            if hit is None:
                continue
            if isinstance(hit, tuple):
                t, u, v = hit
            else:
                t, u, v = hit, 0, 0
            if 1e-6 < t < closest_t:
                closest_t = t
                closest_obj = obj
                #bary_u = u
                #bary_v = v

        # 2) Nic nie trafione -> tło
        if not closest_obj:
            return self.background_color

        # 3) Punkt przecięcia + normalna + kolor obiektu
        hit_point = helpers.multiply_scalar(ray_dir, closest_t)
        hit_point = helpers.add(ray_origin, hit_point)

        # if isinstance(closest_obj, Triangle):
        #     normal = closest_obj.get_normal(hit_point, bary_u, bary_v)
        #     base_color = closest_obj.get_color(bary_u, bary_v)
        #     reflection = closest_obj.reflection
        # else:
        normal = closest_obj.get_normal(hit_point)
        base_color = closest_obj.color
        reflection = getattr(closest_obj, 'reflection', 0.0)

        ambient_color = helpers.multiply_scalar(base_color, self.ambient)

        L = helpers.subtract(self.light_pos, hit_point)
        L = helpers.normalize(L)
        diff = max(helpers.dot(normal, L), 0.0)
        diffuse = helpers.multiply_scalar(base_color, diff * 0.8)
        local_color = helpers.add(ambient_color, diffuse)


        # 5) Odbicie
        if reflection > 0.0 and depth < self.max_depth:
            r = helpers.reflect(ray_dir, normal)
            offset_hit_point = helpers.add(hit_point, helpers.multiply_scalar(normal, 1e-4))
            reflection_col = self.trace_ray(
                ray_origin=offset_hit_point,
                ray_dir=r,
                depth=depth + 1
            )
            local_color = tuple(
                (1.0 - reflection) * local_color[i] + reflection * reflection_col[i]
                for i in range(3)
            )

        return tuple(min(max(c, 0), 255) for c in local_color)