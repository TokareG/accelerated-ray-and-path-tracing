
from typing import List
from core.Utils import *
from core import *
from models import *
import pygame


pygame.init()
width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ray Tracer")
clock = pygame.time.Clock()
running = True

scene = Scene(acceleration_structure="bvh")
scene.load_from_file('data/benchmark.obj')
scene.load_config('./scene_config.json')

camera = Camera(scene, width, height, fov=75)
camera.render()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(camera.canvas, (0, 0))
    pygame.display.flip()
    clock.tick(30)

pygame.quit()