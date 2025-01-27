import argparse
import pygame
from core.Utils import *
from core import *
from models import *


# def parse_args():
#     parser = argparse.ArgumentParser(description="Ray Tracer")
#     parser.add_argument('--acceleration_structure', type=str, default="none", choices=["bvh", "grid", "kd-tree", "mesh_bvh"],
#                         help="Wybór struktury akceleracji.")
#     parser.add_argument('--scene', type=str, required=True, help="Ścieżka do pliku sceny.")
#     parser.add_argument('--scene_config', type=str, required=True, help="Ścieżka do pliku konfiguracji sceny.")
#     parser.add_argument('--width', type=int, default=640, help="Szerokość okna.")
#     parser.add_argument('--height', type=int, default=360, help="Wysokość okna.")
#     return parser.parse_args()

pygame.init()
#args = parse_args()

width, height = 200,200

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ray Tracer")
clock = pygame.time.Clock()
running = True

scene = Scene(acceleration_structure="bvh") #["bvh", "grid", "kd-tree", "mesh_bvh"]
scene.load_from_file('data/scene_2.obj')
scene.load_config('./scene_config.json')

camera = Camera(scene, width, height, fov=80,trace_algorithm="pathtracing") #raytracing, pathtracing
camera.render()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(camera.canvas, (0, 0))
    pygame.display.flip()
    clock.tick(30)

pygame.quit()