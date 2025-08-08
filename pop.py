import pygame
import random
import sys
import os
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🫧Bubble Popper Game!")

# Load background image
try:
    background = pygame.image.load("bgimg.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except pygame.error:
    background = None
    print("Warning: background.jpg not found. Using solid color instead.")

# Load pop sound
try:
    pop_sound = pygame.mixer.Sound("pop.wav")
except pygame.error:
    pop_sound = None
    print("Warning: pop.wav not found. No sound will play.")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUBBLE_COLOR = (135, 206, 235)
RED = (200, 0, 0)
GREEN = (0, 100, 0)

# Font
font = pygame.font.SysFont("Arial", 30)
large_font = pygame.font.SysFont("Arial", 50)

# Reset game state
def reset_game():
    global bubbles, popped, missed_bubbles, game_over, time_elapsed, global_speed_multiplier

    popped = 0
    missed_bubbles = 0
    game_over = False
    time_elapsed = 0
    global_speed_multiplier = 1.0
    bubbles = []

    for _ in range(bubble_count):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(HEIGHT // 2, HEIGHT)
        radius = random.randint(20, 35)
        speed = random.uniform(0.2, 0.5)
        phase = random.uniform(0, math.pi * 2)
        bubbles.append({
            "x": x,
            "y": y,
            "radius": radius,
            "speed": speed,
            "popping": False,
            "pop_timer": 0,
            "phase": phase
        })

# Draw a realistic bubble with transparency and highlight
def draw_bubble(surface, x, y, radius):
    bubble_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    center = (radius, radius)
    pygame.draw.circle(bubble_surface, (135, 206, 235, 100), center, radius)
    highlight_pos = (int(radius * 0.6), int(radius * 0.6))
    pygame.draw.circle(bubble_surface, (255, 255, 255, 180), highlight_pos, radius // 5)
    pygame.draw.circle(bubble_surface, (255, 255, 255, 40), center, radius, width=2)
    surface.blit(bubble_surface, (x - radius, y - radius))

# Button draw function
def draw_button(surface, rect, text, color, hover_color, mouse_pos):
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, hover_color, rect)
    else:
        pygame.draw.rect(surface, color, rect)
    label = font.render(text, True, WHITE)
    surface.blit(label, (rect.x + (rect.width - label.get_width()) // 2,
                         rect.y + (rect.height - label.get_height()) // 2))

# Game state variables
bubble_count = 20
clock = pygame.time.Clock()
running = True
miss_limit = 10
reset_game()

# Try Again button
button_width, button_height = 200, 50
button_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2 + 80, button_width, button_height)

# Main game loop
while running:
    dt = clock.tick(60)
    time_elapsed += dt / 1000.0

    # Increase bubble speed over time
    global_speed_multiplier = 1.0 + (time_elapsed / 60.0)

    # Draw background
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill((200, 230, 255))

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Bubble popping
        if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for bubble in bubbles:
                if not bubble["popping"]:
                    dx = mx - bubble["x"]
                    dy = my - bubble["y"]
                    if dx * dx + dy * dy < bubble["radius"] * bubble["radius"]:
                        bubble["popping"] = True
                        bubble["pop_timer"] = 10
                        popped += 1
                        if pop_sound:
                            pop_sound.play()

        # Try Again button click
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                reset_game()

    if not game_over:
        for bubble in bubbles[:]:
            if not bubble["popping"]:
                bubble["y"] -= bubble["speed"] * global_speed_multiplier
                bubble["x"] += math.sin(time_elapsed * 2 + bubble["phase"]) * 0.5

                if bubble["y"] + bubble["radius"] < 0:
                    bubbles.remove(bubble)
                    missed_bubbles += 1
                    continue

                draw_bubble(screen, bubble["x"], bubble["y"], bubble["radius"])
            else:
                bubble["pop_timer"] -= 1
                scale = bubble["radius"] * (bubble["pop_timer"] / 10)
                if scale > 0:
                    pygame.draw.circle(screen, (0, 191, 255), (int(bubble["x"]), int(bubble["y"])), int(scale))
                if bubble["pop_timer"] <= 0:
                    bubbles.remove(bubble)

        # Add new bubbles
        if len(bubbles) < bubble_count:
            x = random.randint(50, WIDTH - 50)
            y = HEIGHT + random.randint(20, 100)
            radius = random.randint(20, 35)
            speed = random.uniform(0.2, 0.5)
            phase = random.uniform(0, math.pi * 2)
            bubbles.append({
                "x": x,
                "y": y,
                "radius": radius,
                "speed": speed,
                "popping": False,
                "pop_timer": 0,
                "phase": phase
            })

        if missed_bubbles >= miss_limit:
            game_over = True

    # Score display
    screen.blit(font.render(f"Popped: {popped}", True, BLACK), (10, 10))
    screen.blit(font.render(f"Missed: {missed_bubbles}/{miss_limit}", True, RED), (10, 50))

    if game_over:
        # Game Over text
        over_text = large_font.render("Game Over!", True, RED)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 30))
        sub_text = font.render("Too many bubbles escaped!", True, BLACK)
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 30))

        # Draw Try Again button
        draw_button(screen, button_rect, "Try Again", GREEN, (0, 255, 0), mouse_pos)

    pygame.display.flip()

pygame.quit()
sys.exit()
