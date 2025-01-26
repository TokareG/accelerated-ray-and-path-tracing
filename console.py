import pygame
import subprocess
import threading
import psutil
import time
import tkinter as tk
from tkinter import filedialog

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
WIDTH, HEIGHT = 720, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Program Tester")

# Kolory
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

# Czcionka
font = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Funkcja do monitorowania subprocessa i jego zasobów
def run_program(program_path, args):
    process = subprocess.Popen(["python", program_path] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    return stdout.decode(), stderr.decode()

# Funkcja do obliczania rozmieszczenia przycisków
def calculate_button_positions(num_buttons, button_height, vertical_padding, total_height):
    button_positions = []
    total_padding = vertical_padding * (num_buttons - 1)
    total_buttons_height = button_height * num_buttons + total_padding
    starting_y = (total_height - total_buttons_height) // 2 - 70

    for i in range(num_buttons):
        button_positions.append(starting_y + i * (button_height + vertical_padding))
    
    return button_positions

# Przyciski
button_rects = [pygame.Rect((WIDTH - 250) // 2, 0, 250, 50) for _ in range(7)]

# Ścieżki do testowanych programów
program_path = "main.py"

# Zmienne globalne
none_selected = False  # Add new variable
bvh_selected = False
kd_selected = False
uniformg_selected = False
scene_file = "Wybierz Scenę"
scene_config_file = "Konfiguracja"
width = "800"
height = "600"

def select_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Wybierz plik")

def start_program(acceleration_structure):
    global scene_file, scene_config_file, width, height
    if scene_file and scene_config_file:
        args = [
            '--acceleration_structure', acceleration_structure,
            '--scene', scene_file,
            '--scene_config', scene_config_file,
            '--width', width,
            '--height', height
        ]
        stdout, stderr = run_program(program_path, args)
        return stdout, stderr
    else:
        return None, None, "Brak wybranych plików", "Brak wybranych plików"

# Pętla główna
running = True
button_height = 50
vertical_padding = 20
button_positions = calculate_button_positions(len(button_rects), button_height, vertical_padding, HEIGHT)

input_boxes = [
    pygame.Rect((WIDTH - 200) // 2, button_positions[-1] + 70, 200, 50),
    pygame.Rect((WIDTH - 200) // 2, button_positions[-1] + 130, 200, 50)
]
active_input = None
input_texts = [width, height]

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rects[0].collidepoint(event.pos):
                bvh_selected = not bvh_selected
            elif button_rects[1].collidepoint(event.pos):
                kd_selected = not kd_selected
            elif button_rects[2].collidepoint(event.pos):
                uniformg_selected = not uniformg_selected
            elif button_rects[3].collidepoint(event.pos):
                none_selected = not none_selected  
            elif button_rects[4].collidepoint(event.pos):
                scene_file = select_file()
            elif button_rects[5].collidepoint(event.pos):
                scene_config_file = select_file()
            elif button_rects[6].collidepoint(event.pos):  
                if bvh_selected:
                    start_program("bvh")
                if kd_selected:
                    start_program("kdtree")
                if uniformg_selected:
                    start_program("uniform_grid")
                if none_selected:
                    start_program("none")
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
            pygame.draw.rect(screen, LIGHT_BLUE if bvh_selected else DARK_BLUE, button_rect)
            text = font.render("Render BVH", True, WHITE)
        elif i == 1:
            pygame.draw.rect(screen, LIGHT_BLUE if kd_selected else DARK_BLUE, button_rect)
            text = font.render("Render KD-T", True, WHITE)
        elif i == 2:
            pygame.draw.rect(screen, LIGHT_BLUE if uniformg_selected else DARK_BLUE, button_rect)
            text = font.render("Render UniformG", True, WHITE)
        elif i == 3:
            pygame.draw.rect(screen, LIGHT_BLUE if none_selected else DARK_BLUE, button_rect)
            text = font.render("No Structure", True, WHITE)
        elif i == 4:
            pygame.draw.rect(screen, ORANGE, button_rect)
            text = font.render(scene_file, True, WHITE)
        elif i == 5:
            pygame.draw.rect(screen, PURPLE, button_rect)
            text = font.render(scene_config_file, True, WHITE)
        elif i == 6:  
            pygame.draw.rect(screen, LIGHT_GREEN if (bvh_selected or kd_selected or uniformg_selected or none_selected) else DARK_GREEN, button_rect)
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

        # Dodanie napisów "Szerokość" i "Wysokość"
        if i == 0:
            label = font.render("Szerokość", True, BLACK)
            screen.blit(label, (box.x - label.get_width() - 10, box.y + (box.height - label.get_height()) // 2))
        elif i == 1:
            label = font.render("Wysokość", True, BLACK)
            screen.blit(label, (box.x - label.get_width() - 10, box.y + (box.height - label.get_height()) // 2))

    pygame.display.flip()

    width, height = input_texts

pygame.quit()