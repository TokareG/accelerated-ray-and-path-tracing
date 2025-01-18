import numpy as np
import pygame
from core.helpers import *
class RayTracer:
    """
    The class responsible for configuring the camera and rendering properly
    to the Pygame surface.
    """
    def __init__(self, scene, width, height, camera_origin,fov):
        self.scene = scene
        self.width = width
        self.height = height
        self.camera_origin = np.array(camera_origin, dtype=float)
        self.fov = fov
        self.pixel_surf = pygame.Surface((width, height))

    def render(self):
        """
        Main rendering loop (ray casting) - fills self.pixel_surf.
        """
        print("Rendering...")
        for y in range(self.height):
            for x in range(self.width):
                # coordinates in the [-1..1] system, including fov
                u = (x / self.width)*2.0 - 1.0
                v = (y / self.height)*2.0 - 1.0
                u *= self.fov
                v *= self.fov * (self.height / self.width)

                ray_dir = np.array([u, -v, 0], dtype=float) - self.camera_origin
                ray_dir = helpers.normalize(ray_dir)

                color = self.scene.trace_ray(
                    ray_origin=self.camera_origin,
                    ray_dir=ray_dir,
                    depth=0
                )
                self.pixel_surf.set_at((x, y), tuple(int(c) for c in color))
        print("Render done.")

    def get_surface(self):
        """
        Returns the rendered Pygame surface (Surface).
        """
        return self.pixel_surf
