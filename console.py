import pygame
import subprocess
import tkinter as tk
from tkinter import filedialog
import os
import matplotlib.pyplot as plt

# Initialize Pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Program Tester")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (0, 51, 102)
LIGHT_BLUE = (51, 153, 255)
ORANGE = (255, 128, 0)
DARK_GREEN = (0, 102, 51)
LIGHT_GREEN = (51, 204, 51)
PURPLE = (102, 0, 153)
GREY = (200, 200, 200)
DARK_RED = (153, 0, 0)
LIGHT_RED = (255, 51, 51)

# Fonts
font = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Function to run a subprocess and capture its output
def run_program(program_path, args):
    process = subprocess.Popen(["python", program_path] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode(), stderr.decode()

# Function to calculate button positions
def calculate_button_positions(num_buttons, button_height, vertical_padding, total_height):
    button_positions = []
    total_padding = vertical_padding * (num_buttons - 1)
    total_buttons_height = button_height * num_buttons + total_padding
    starting_y = (total_height - total_buttons_height) // 2 - 70

    for i in range(num_buttons):
        button_positions.append(starting_y + i * (button_height + vertical_padding))
    
    return button_positions

# Function to read efficiency results and plot graphs
def check_results():
    directory = "Efficiency_results"
    render_times = {}
    pixels_per_second = {}
    ram_usage = {}

    for filename in os.listdir(directory):
        if filename.endswith("_efficiency.txt"):
            with open(os.path.join(directory, filename), 'r') as file:
                lines = file.readlines()
                render_time = float(lines[0].split(":")[1].strip().replace("seconds", ""))
                pps = int(lines[1].split(":")[1].strip().replace("pps", ""))
                ram = float(lines[2].split(":")[1].strip().replace("MB", ""))
                key = filename.replace("_efficiency.txt", "")
                render_times[key] = render_time
                pixels_per_second[key] = pps
                ram_usage[key] = ram

    # Plot render times
    plt.figure(figsize=(10, 5))
    bars = plt.bar(render_times.keys(), render_times.values(), color='blue')
    plt.xlabel('Acceleration Structures')
    plt.ylabel('Render Time (seconds)')
    plt.title('Render Time Comparison')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')
    plt.show(block=False)

    # Plot pixels per second
    plt.figure(figsize=(10, 5))
    bars = plt.bar(pixels_per_second.keys(), pixels_per_second.values(), color='green')
    plt.xlabel('Acceleration Structures')
    plt.ylabel('Pixels per Second (pps)')
    plt.title('Pixels per Second Comparison')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, yval, ha='center', va='bottom')
    plt.show(block=False)

    # Plot average RAM usage
    plt.figure(figsize=(10, 5))
    bars = plt.bar(ram_usage.keys(), ram_usage.values(), color='orange')
    plt.xlabel('Acceleration Structures')
    plt.ylabel('Average RAM Usage (MB)')
    plt.title('Average RAM Usage During Rendering')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')
    plt.show(block=False)

# Function to delete all files in the Efficiency_results directory
def delete_results():
    directory = "Efficiency_results"
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Button rectangles
button_rects = [pygame.Rect((WIDTH - 250) // 2, 0, 250, 50) for _ in range(10)]
check_results_button_rect = pygame.Rect(WIDTH - 200, 10, 190, 40)
delete_results_button_rect = pygame.Rect(WIDTH - 200, 60, 190, 40)

# Path to the program being tested
program_path = "main.py"

# Global variables
raytracing_selected = True  # Default to raytracing
pathtracing_selected = False
bvh_mesh_selected = False  # Add new variable
bvh_selected = False
kd_selected = False
uniformg_selected = False
no_structure_selected = False  # New variable for "No Structure"
scene_file = "Wybierz Scenę"
scene_file_path = ""
scene_config_file = "Konfiguracja"
scene_config_file_path = ""
width = "800"
height = "600"
fov = "60"

# Function to open a file dialog and select a file
def select_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Wybierz plik")

# Function to start the program with the selected acceleration structure
def start_program(acceleration_structure):
    global scene_file_path, scene_config_file_path, width, height
    if scene_file_path and scene_config_file_path:
        trace_algo = "raytracing" if raytracing_selected else "pathtracing"
        args = [
            '--acceleration_structure', acceleration_structure,
            '--scene', scene_file_path,
            '--scene_config', scene_config_file_path,
            '--width', width,
            '--height', height,
            '--fov', fov,
            '--trace_algorithm', trace_algo
        ]
        stdout, stderr = run_program(program_path, args)
        return stdout, stderr
    else:
        return None, None, "Brak wybranych plików", "Brak wybranych plików"

# Main loop
running = True
button_height = 50
vertical_padding = 20
button_positions = calculate_button_positions(len(button_rects), button_height, vertical_padding, HEIGHT)

# Input boxes for width and height
input_boxes = [
    pygame.Rect((WIDTH - 200) // 2, button_positions[-1] + 70, 200, 50),
    pygame.Rect((WIDTH - 200) // 2, button_positions[-1] + 130, 200, 50),
    pygame.Rect((WIDTH - 200) // 2, button_positions[-1] + 190, 200, 50)
]
active_input = None
input_texts = [width, height, fov]

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rects[0].collidepoint(event.pos):
                raytracing_selected = True
                pathtracing_selected = False
            elif button_rects[1].collidepoint(event.pos):
                raytracing_selected = False
                pathtracing_selected = True
            elif button_rects[2].collidepoint(event.pos):
                bvh_selected = not bvh_selected
            elif button_rects[3].collidepoint(event.pos):
                kd_selected = not kd_selected
            elif button_rects[4].collidepoint(event.pos):
                uniformg_selected = not uniformg_selected
            elif button_rects[5].collidepoint(event.pos):
                bvh_mesh_selected = not bvh_mesh_selected  
            elif button_rects[6].collidepoint(event.pos):
                no_structure_selected = not no_structure_selected  # Toggle no_structure_selected
            elif button_rects[7].collidepoint(event.pos):
                scene_file_path = select_file()
                scene_file = os.path.basename(scene_file_path)
            elif button_rects[8].collidepoint(event.pos):
                scene_config_file_path = select_file()
                scene_config_file = os.path.basename(scene_config_file_path)
            elif button_rects[9].collidepoint(event.pos):  
                if bvh_selected:
                    start_program("bvh")
                if kd_selected:
                    start_program("kd-tree")
                if uniformg_selected:
                    start_program("grid")
                if bvh_mesh_selected:
                    start_program("mesh_bvh")
                if no_structure_selected:
                    start_program("no-structure")
            elif check_results_button_rect.collidepoint(event.pos):
                check_results()
            elif delete_results_button_rect.collidepoint(event.pos):
                delete_results()
            for i, box in enumerate(input_boxes):
                if box.collidepoint(event.pos):
                    active_input = i
                    break
            else:
                active_input = None
        elif event.type == pygame.KEYDOWN and active_input is not None:
            if event.key == pygame.K_BACKSPACE:
                input_texts[active_input] = input_texts[active_input][:-1]
            else:
                input_texts[active_input] += event.unicode

    for i, button_rect in enumerate(button_rects):
        button_rect.y = button_positions[i]
        if i == 0:
            pygame.draw.rect(screen, LIGHT_GREEN if raytracing_selected else DARK_GREEN, button_rect)
            text = font.render("RayTracing", True, WHITE)
        elif i == 1:
            pygame.draw.rect(screen, LIGHT_GREEN if pathtracing_selected else DARK_GREEN, button_rect)
            text = font.render("PathTracing", True, WHITE)
        elif i == 2:
            pygame.draw.rect(screen, LIGHT_BLUE if bvh_selected else DARK_BLUE, button_rect)
            text = font.render("Render BVH", True, WHITE)
        elif i == 3:
            pygame.draw.rect(screen, LIGHT_BLUE if kd_selected else DARK_BLUE, button_rect)
            text = font.render("Render KD-Tree", True, WHITE)
        elif i == 4:
            pygame.draw.rect(screen, LIGHT_BLUE if uniformg_selected else DARK_BLUE, button_rect)
            text = font.render("Render Uniform", True, WHITE)
        elif i == 5:
            pygame.draw.rect(screen, LIGHT_BLUE if bvh_mesh_selected else DARK_BLUE, button_rect)
            text = font.render("Render BVH-M", True, WHITE)
        elif i == 6:
            pygame.draw.rect(screen, LIGHT_BLUE if no_structure_selected else DARK_BLUE, button_rect)
            text = font.render("No Structure", True, WHITE)
        elif i == 7:
            pygame.draw.rect(screen, ORANGE, button_rect)
            text = font.render(scene_file, True, WHITE)
        elif i == 8:
            pygame.draw.rect(screen, PURPLE, button_rect)
            text = font.render(scene_config_file, True, WHITE)
        elif i == 9:  
            pygame.draw.rect(screen, LIGHT_GREEN if (bvh_selected or kd_selected or uniformg_selected or bvh_mesh_selected or no_structure_selected) else DARK_GREEN, button_rect)
            text = font.render("Start", True, WHITE)

        screen.blit(
            text,
            (button_rect.x + (button_rect.width - text.get_width()) // 2,
             button_rect.y + (button_rect.height - text.get_height()) // 2)
        )

    for i, box in enumerate(input_boxes):
        pygame.draw.rect(screen, GREY, box)
        text_surface = font.render(input_texts[i], True, BLACK)
        text_x = box.x + (box.width - text_surface.get_width()) // 2
        text_y = box.y + (box.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        pygame.draw.rect(screen, BLACK, box, 2)

        # Add labels "Width" and "Height"
                # Add labels
        if i == 0:
            label = font.render("Szerokość", True, BLACK)
            screen.blit(label, (box.x - label.get_width() - 10, box.y + (box.height - label.get_height()) // 2))
        elif i == 1:
            label = font.render("Wysokość", True, BLACK)
            screen.blit(label, (box.x - label.get_width() - 10, box.y + (box.height - label.get_height()) // 2))
        elif i == 2:
            label = font.render("FOV", True, BLACK)
            screen.blit(label, (box.x - label.get_width() - 10, box.y + (box.height - label.get_height()) // 2))

    # Draw "Check results" button
    pygame.draw.rect(screen, ORANGE, check_results_button_rect)
    text = font.render("Check results", True, WHITE)
    screen.blit(text, (check_results_button_rect.x + (check_results_button_rect.width - text.get_width()) // 2,
                       check_results_button_rect.y + (check_results_button_rect.height - text.get_height()) // 2))

    # Draw "Delete Results" button
    pygame.draw.rect(screen, DARK_RED, delete_results_button_rect)
    text = font.render("Delete Results", True, WHITE)
    screen.blit(text, (delete_results_button_rect.x + (delete_results_button_rect.width - text.get_width()) // 2,
                       delete_results_button_rect.y + (delete_results_button_rect.height - text.get_height()) // 2))

    pygame.display.flip()

    width, height, fov = input_texts

pygame.quit()