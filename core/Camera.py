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
                 img_width: int = 300,
                 img_height: int = 200,
                 camera_origin: List[float] = (0,0,8) , #,Scene_3:(0,0,8) Scene_2:(0,.75,0)
                 lookat: List[float] = (0,.0,-1), #Scene_3:(0,.0,-1),Scene_2:(0,.75,-1)
                 vup: List[float] =(0,1,0),
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
        
        viewport_u = scale(self.viewport_width, u)
        viewport_v = scale(-self.viewport_heigh, v)
        
        self.pixel_delta_u = div_by_scalar(viewport_u, img_width)
        self.pixel_delta_v = div_by_scalar(viewport_v, img_height)

        viewport_upper_left = sub(sub(camera_origin,w), add(div_by_scalar(viewport_u, 2), div_by_scalar(viewport_v, 2)))
        self.pixel_00 = add(viewport_upper_left, scale(0.5, add(self.pixel_delta_u, self.pixel_delta_v)))

    def get_ray(self, i: int, j: int):
        """
        Generates a ray originating from the camera and passing through the pixel at (i, j).
        """

        offset_x = random.gauss(0,1) - 1
        offset_y = random.gauss(0,1) - 1
        pixel_sample = add(self.pixel_00, add(scale(i + offset_x, self.pixel_delta_u), scale(j + offset_y, self.pixel_delta_v)))
        ray_direction = sub(pixel_sample, self.camera_origin)
        return Ray(self.camera_origin, ray_direction)


    def render(self):
        """
        Renders the scene by casting rays through each pixel and determining their colors based on scene intersections.
        The rendered image is displayed on the Pygame surface.
        """
        total_pixels = self.img_height * self.img_width
        with tqdm(total=total_pixels, desc="Rendering", unit="pixel") as pbar:
            for j in range(self.img_height):
                for i in range(self.img_width):
                    pixel_color = [0,0,0]
                    for sample in range(5): #TODO: various number of samples per pixel
                        ray = self.get_ray(i,j)
                        color = self.get_color(ray)
                        #result = self.scene.hit(ray)
                        #hit, inter, color = result if result else (False, None, None)
                        #if hit:
                        pixel_color = add(pixel_color, color)
                    pixel_color = [min(255, max(0, val*255/5)) for val in pixel_color]
                    self.canvas.set_at((i, j), pixel_color)
                    
                    pbar.update(1)

    def get_color(self, ray):
        hit = self.scene.hit(ray)
        if hit:
            t, intersection_point, face = hit
            if face.material.illumination_model == 2:
                # Zaczynamy od światła otoczenia (ambient):
                out_color = scale(self.scene.ambient_light, face.material.ambient)

                for light in self.scene.lights:
                    # Dla każdego światła sprawdzamy, czy jest zasłonięte
                    light_ray = Ray(add(intersection_point, scale(1e-3, face.unit_norm)),
                                    norm(sub(light.position, intersection_point)))
                    t_to_light = sum(x ** 2 for x in sub(light.position, intersection_point)) ** (1 / 2)
                    light_hit = self.scene.hit(light_ray)

                    if light_hit:
                        light_t, _, _ = light_hit
                        if light_t < t_to_light:
                            # Jeśli zasłonięte -> dajemy tylko ambient, więc w tym świetle nic nie dodajemy
                            continue
                            # ewentualnie można dodać bardzo delikatny "przesiany" kolor, zależnie od materiału
                    # Jeśli nie zasłonięte:
                    out_color = add(out_color, self.phong(face, light, intersection_point))

                return out_color
            if face.material.illumination_model == 3:
                direction = sub(ray.direction, scale(2 * dot(ray.direction, face.unit_norm), face.unit_norm))
                reflected_ray = Ray(intersection_point, direction)
                return matmul(self.get_color(reflected_ray), face.material.diffuse)
                #return add(self.phong(face, self.scene.lights[0], intersection_point) , scale(0.7, self.get_color(reflected_ray)))

        unit_ray_direction = norm(ray.direction)
        a = 0.5 * (unit_ray_direction[1] + 1)
        return add(scale(1.0-a, [1,1,1]), scale(a, [0.5,0.7,1.0]))
        #return [0,0,0]

    def phong(self, face, light, intersection_point) -> List[float]:
        Ns, ka, kd, ks, Ni, d, illum = (face.material.shininess,
                                        face.material.ambient,
                                        face.material.diffuse,
                                        face.material.specular,
                                        face.material.optical_density,
                                        face.material.transparency,
                                        face.material.illumination_model)
        L = norm(sub(light.position, intersection_point))
        R = norm(sub(scale(2 * dot(face.unit_norm, L), face.unit_norm), L))
        V = norm(sub([0, 0, 0], intersection_point))
        color = add(scale(self.scene.ambient_light, ka), scale(light.intensity, matmul(light.color, add(scale(
            max(0, dot(L, face.unit_norm)), kd), scale(max(0, dot(R, V)) ** Ns, ks)))))
        return color