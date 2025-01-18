from models import *
from core import *
import pygame


s = Sphere((1,1,1), 0.5, (255,0,0), 0.6, 0.1, 1.0)
p= Plane((0,-1,0),(0,1,0),(100,200,100),0.2, 0.0, 1.0)
b=Box((-0.5,0.0,1.0),(0.5,1.0,2.0),(200,200,50),0.3,0.0,1.0)

if __name__ == "__main__":
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Ray Tracer")
    clock = pygame.time.Clock()
    running = True

    scene = Scene((5, 5, -3),(0, 0, 0),0.2,3)
    scene.add_object(p)
    scene.add_object(s)
    scene.add_object(b)

    raytracer = RayTracer(scene, width, height, (0,1,-6),2.0)
    raytracer.render()




    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(raytracer.get_surface(), (0, 0))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
