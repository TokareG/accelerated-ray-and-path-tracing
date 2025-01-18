from models import *
from core import *
import pygame
import numpy as np

s = Sphere((1,1,1), 0.5, (255,255,255), 0.1, 0.1, 0)
p= Plane((0,-1,0),(0,1,0),(100,200,100),0.2, 0.0, 1.0)
b=Box((-0.5,0.0,1.0),(0.5,1.0,2.0),(200,200,50),0.3,0.0,1.0)

if __name__ == "__main__":
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Ray Tracer")

    clock = pygame.time.Clock()
    running = True

    scene = Scene((5, 5, -3),(50, 50, 200),0.2,3)

    scene.add_object(p)
    scene.add_object(s)
    scene.add_object(b)
    camera_origin = np.array([0, 1, -6], dtype=float)
    raytracer = RayTracer(scene, width, height, camera_origin,2.0)
    raytracer.render()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(raytracer.get_surface(), (0, 0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
