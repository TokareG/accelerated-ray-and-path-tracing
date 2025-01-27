import argparse
import pygame
import timeit
import os
import psutil  # Dodane do monitorowania pamięci
from core.Utils import *
from core import *
from models import *

# Parse arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Ray Tracer")
    parser.add_argument('--trace_algorithm', type=str, default="raytracing", choices=["raytracing", "pathtracing"],
                        help="Wybór algorytmu śledzenia promieni")
    parser.add_argument('--acceleration_structure', type=str, default="none", choices=["bvh", "grid", "kd-tree", "mesh_bvh", "no-structure"],
                        help="Wybór struktury akceleracji.")
    parser.add_argument('--scene', type=str, required=True, help="Ścieżka do pliku sceny.")
    parser.add_argument('--scene_config', type=str, required=True, help="Ścieżka do pliku konfiguracji sceny.")
    parser.add_argument('--width', type=int, default=640, help="Szerokość okna.")
    parser.add_argument('--height', type=int, default=360, help="Wysokość okna.")
    parser.add_argument('--fov', type=float, default=60, help="Pole widzenia kamery.")
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

camera = Camera(scene, width, height, fov=args.fov, trace_algorithm=args.trace_algorithm)

# Monitor RAM usage
process = psutil.Process(os.getpid())

# Pomiar zużycia pamięci RAM przed renderingiem
initial_memory = process.memory_info().rss

# Measure rendering time
render_time = timeit.timeit(lambda: camera.render(), number=1)

# Pomiar zużycia pamięci RAM po renderingu
final_memory = process.memory_info().rss
average_memory_usage = (initial_memory + final_memory) / 2 / (1024 * 1024)  # w MB

#Calculate Pixels per second
total_pixels = camera.img_height * camera.img_width
pps = total_pixels / render_time

output_dir = "Efficiency_results"
os.makedirs(output_dir, exist_ok=True)

# Save results to a single file
efficiency_filename = os.path.join(output_dir, f"{args.trace_algorithm}_{args.acceleration_structure}_efficiency.txt")
with open(efficiency_filename, "w") as f:
    f.write(f"Render time: {render_time:.6f} seconds\n")
    f.write(f"Average Pixels per second: {pps:.0f} pps\n")
    f.write(f"Average RAM usage during rendering: {average_memory_usage:.2f} MB\n")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(camera.canvas, (0, 0))
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
