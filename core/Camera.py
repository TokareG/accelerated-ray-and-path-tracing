import pygame
from core.Utils import *
from core import *
from models import *
from typing import Tuple, List
import math
import random
import time
from tqdm import tqdm

class Camera:
    """
    The Camera class is responsible for configuring the camera settings and rendering the scene
    onto a Pygame surface. It handles the generation of rays for each pixel, performing ray tracing
    to determine pixel colors based on scene intersections.

    Args:
        scene (Scene): The 3D scene to be rendered.
        img_width (int, optional): Width of the output image in pixels. Defaults to 400.
        img_height (int, optional): Height of the output image in pixels. Defaults to 300.
        camera_origin (List[float], optional): The position of the camera in 3D space. Defaults to (0, 0, 2).
        lookat (List[float], optional): The point in space the camera is looking at. Defaults to (0, 0, -1).
        vup (List[float], optional): The "up" direction for the camera, defining the camera's orientation. Defaults to (0, 1, 0).
        fov (int, optional): Field of view in degrees. Determines the extent of the observable world. Defaults to 60.
    """
    def __init__(self,
                 scene: Scene,
                 img_width: int = 400,
                 img_height: int = 300,
                 camera_origin: List[float] = (0,0,2),
                 lookat: List[float] = (0,0,-1),
                 vup: List[float] = (0,1,0),
                 fov: int = 60):
        self.scene = scene
        self.img_width = img_width
        self.img_height = img_height
        self.camera_origin = tuple(camera_origin)
        self.fov = fov
        self.canvas = pygame.Surface((img_width, img_height))

        theta = math.radians(fov)
        half_width = math.tan(theta/2)
        self.viewport_width = 2* half_width
        self.viewport_heigh = self.viewport_width * (img_height/img_width)

        w = norm(sub(camera_origin, lookat))
        u = norm(cross(vup, w))
        v = cross(w, u)
        
        viewport_u = scalmul(self.viewport_width, u)
        viewport_v = scalmul(-self.viewport_heigh, v)
        
        self.pixel_delta_u = div_by_scalar(viewport_u, img_width)
        self.pixel_delta_v = div_by_scalar(viewport_v, img_height)

        viewport_upper_left = sub(sub(camera_origin,w), add(div_by_scalar(viewport_u, 2), div_by_scalar(viewport_v, 2)))
        self.pixel_00 = add(viewport_upper_left, scalmul(0.5, add(self.pixel_delta_u, self.pixel_delta_v)))

    def get_ray(self, i: int, j: int):
        """
        Generates a ray originating from the camera and passing through the pixel at (i, j).
        """

        offset_x = random.gauss(0,1) - 1
        offset_y = random.gauss(0,1) - 1
        pixel_sample = add(self.pixel_00, add(scalmul(i + offset_x, self.pixel_delta_u), scalmul(j + offset_y, self.pixel_delta_v)))
        ray_direction = sub(pixel_sample, self.camera_origin)
        return Ray(self.camera_origin, ray_direction)


    def render(self):
        """
        Renders the scene by casting rays through each pixel and determining their colors based on scene intersections.
        The rendered image is displayed on the Pygame surface.
        """
        start = time.process_time()
        total_pixels = self.img_height * self.img_width
        with tqdm(total=total_pixels, desc="Rendering", unit="pixel") as pbar:
            for j in range(self.img_height):
                for i in range(self.img_width):
                    #print(f"Rendering pixel ({i}, {j})")
                    pixel_color = [0,0,0]
                    for sample in range(4): #TODO: various number of samples per pixel
                        ray = self.get_ray(i,j)
                        result = self.scene.hit(ray)
                        hit, inter,  color = result if result else (False, None, None)
                        if hit:
                            pixel_color = add(pixel_color, color)
                        
                    self.canvas.set_at((i, j), scalmul(1/4, pixel_color))
                    
                    pbar.update(1)