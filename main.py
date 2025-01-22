
from typing import List
from core.Utils import *
from core import *
from models import *
import pygame


pygame.init()
width, height = 400, 300
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ray Tracer")
clock = pygame.time.Clock()
running = True

scene = Scene()
scene.load_from_file('data/scene_1.obj')

camera = Camera(scene)
camera.render()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(camera.canvas, (0, 0))
    pygame.display.flip()
    clock.tick(30)

pygame.quit()