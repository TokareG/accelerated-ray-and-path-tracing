import argparse
import pygame
from core.Utils import *
from core import *
from models import *
import pygame


def parse_args():
    parser = argparse.ArgumentParser(description="Ray Tracer")
    parser.add_argument('--acceleration_structure', type=str, default="none", choices=["bvh", "grid", "kd-tree", "mesh_bvh"],
                        help="Wybór struktury akceleracji.")
    parser.add_argument('--scene', type=str, required=True, help="Ścieżka do pliku sceny.")
    parser.add_argument('--scene_config', type=str, required=True, help="Ścieżka do pliku konfiguracji sceny.")
    parser.add_argument('--width', type=int, default=640, help="Szerokość okna.")
    parser.add_argument('--height', type=int, default=360, help="Wysokość okna.")
    return parser.parse_args()

pygame.init()
args = parse_args()

width, height = args.width, args.height

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ray Tracer")
clock = pygame.time.Clock()
running = True

scene = Scene(acceleration_structure=args.acceleration_structure)
scene.load_from_file(args.scene)
scene.load_config(args.scene_config)

camera = Camera(scene, width, height)
camera.render()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(camera.canvas, (0, 0))
    pygame.display.flip()
    clock.tick(30)

pygame.quit()