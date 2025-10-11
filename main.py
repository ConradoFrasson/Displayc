import os
import math
import pygame
import random
import time

# --- Constants ---
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (200, 200, 200)

# Screen dimensions
WIDTH, HEIGHT = 1280, 720

# --- Data Simulation ---
def get_simulated_data():
    """Returns a dictionary of simulated car data."""
    return {
        'rpm': random.randint(1000, 12000),
        'speed': random.randint(0, 250),
        'soc': random.uniform(0, 100),
        'power': random.uniform(-60, 0),
        'bat_temp': random.randint(20, 80),
        'mot_temp': random.randint(20, 110),
        'throttle': random.uniform(0, 100),
        'brake': random.uniform(0, 100),
        'tires': {
            'FL': {'temp': random.randint(50, 60), 'psi': random.randint(8, 12), 'wear': random.uniform(0, 100)},
            'FR': {'temp': random.randint(50, 60), 'psi': random.randint(8, 12), 'wear': random.uniform(0, 100)},
            'RL': {'temp': random.randint(50, 60), 'psi': random.randint(8, 12), 'wear': random.uniform(0, 100)},
            'RR': {'temp': random.randint(50, 60), 'psi': random.randint(8, 12), 'wear': random.uniform(0, 100)},
        },
        'lap_times': {
            'best': "1:25:123",
            'previous': "1:25:123",
            'current': "1:25:123",
        },
        'status': {
            'bms': random.choice(['perfect', 'good', 'warning', 'failure']),
            'battery': random.choice(['perfect', 'good', 'warning', 'failure']),
            'engine': random.choice(['perfect', 'good', 'warning', 'failure']),
        }
    }

# --- UI Drawing Functions ---
def draw_separators(surface):
    """Draws the separator lines."""
    # Main vertical
    pygame.draw.line(surface, WHITE, (350, 100), (350, 700), 2)
    # Main horizontal
    pygame.draw.line(surface, WHITE, (350, 500), (1280, 500), 2)
    # Center horizontal
    pygame.draw.line(surface, WHITE, (350, 250), (900, 250), 2)
    # Center vertical
    pygame.draw.line(surface, WHITE, (900, 100), (900, 500), 2)

def draw_rpm_speed(surface, data):
    """Draws the RPM and Speed readouts and RPM lights."""
    font_large = pygame.font.Font(None, 150)
    font_small = pygame.font.Font(None, 30)
    font_very_small = pygame.font.Font(None, 20)

    # RPM and Speed Labels
    rpm_label = font_small.render("RPM", True, WHITE)
    surface.blit(rpm_label, (640 - rpm_label.get_width() // 2, 220))
    kmh_label = font_small.render("Km/h", True, WHITE)
    surface.blit(kmh_label, (640 - kmh_label.get_width() // 2, 420))
    endurance_label = font_very_small.render("Endurance Mode", True, ORANGE)
    surface.blit(endurance_label, (640 - endurance_label.get_width() // 2, 450))

    # RPM and Speed
    rpm_text = font_large.render(f"{data['rpm']}", True, RED)
    rpm_rect = rpm_text.get_rect(center=(640, 150))
    surface.blit(rpm_text, rpm_rect)
    speed_text = font_large.render(f"{data['speed']}", True, WHITE)
    speed_rect = speed_text.get_rect(center=(640, 350))
    surface.blit(speed_text, speed_rect)

    # RPM Lights
    rpm_ratio = data['rpm'] / 12000
    for i in range(16):
        color = BLACK
        if rpm_ratio > (i / 16):
            if i < 4: color = BLUE
            elif i < 8: color = GREEN
            elif i < 12: color = YELLOW
            else: color = RED
        pygame.draw.circle(surface, color, (300 + i * 40, 50), 15)

def draw_temp_gauges(surface, data):
    """Draws the temperature gauges."""
    font_small = pygame.font.Font(None, 30)
    font_very_small = pygame.font.Font(None, 20)

    # BAT
    bat_temp_width = ((data['bat_temp'] - 20) / (80 - 20)) * 150
    pygame.draw.rect(surface, RED, (950, 120, bat_temp_width, 50))
    pygame.draw.rect(surface, WHITE, (950, 120, 150, 50), 2)
    bat_label = font_small.render("BAT", True, WHITE)
    surface.blit(bat_label, (955, 175))
    bat_max = font_very_small.render("80°C", True, WHITE)
    surface.blit(bat_max, (1110, 120))
    bat_min = font_very_small.render("20°C", True, WHITE)
    surface.blit(bat_min, (955, 100))

    # MOT
    mot_temp_width = ((data['mot_temp'] - 20) / (110 - 20)) * 150
    pygame.draw.rect(surface, YELLOW, (950, 200, mot_temp_width, 50))
    pygame.draw.rect(surface, WHITE, (950, 200, 150, 50), 2)
    mot_label = font_small.render("MOT", True, WHITE)
    surface.blit(mot_label, (955, 255))
    mot_max = font_very_small.render("110°C", True, WHITE)
    surface.blit(mot_max, (1110, 200))
    mot_min = font_very_small.render("20°C", True, WHITE)
    surface.blit(mot_min, (955, 180))

def draw_tire_data(surface, data):
    """Draws the tire data."""
    font_very_small = pygame.font.Font(None, 24)
    # Positions are now inside the car diagram placeholder
    tire_positions = {'FL': (40, 120), 'FR': (260, 120), 'RL': (40, 420), 'RR': (260, 420)}
    for pos, (x, y) in tire_positions.items():
        temp_text = font_very_small.render(f"{data['tires'][pos]['temp']}°C", True, WHITE)
        psi_text = font_very_small.render(f"{data['tires'][pos]['psi']}PSI", True, GREEN)
        wear_text = font_very_small.render(f"Wear: {data['tires'][pos]['wear']:.1f}%", True, ORANGE)
        surface.blit(temp_text, (x, y))
        surface.blit(psi_text, (x, y + 20))
        surface.blit(wear_text, (x, y + 40))


def draw_status_box(surface, data):
    """Draws the system status box."""
    font_small = pygame.font.Font(None, 30)
    status_colors = {'perfect': BLUE, 'good': GREEN, 'warning': YELLOW, 'failure': RED}

    y_offset = 550
    for system, status in data['status'].items():
        text = font_small.render(system.upper(), True, WHITE)
        surface.blit(text, (50, y_offset))
        pygame.draw.rect(surface, status_colors.get(status, GRAY), (200, y_offset, 100, 30))
        y_offset += 40

def draw_throttle_brake_bars(surface, data):
    """Draws the throttle and brake bars."""
    font_small = pygame.font.Font(None, 30)

    # Throttle
    throttle_height = (data['throttle'] / 100) * 150
    pygame.draw.rect(surface, GREEN, (950, 450 - throttle_height, 50, throttle_height))
    pygame.draw.rect(surface, WHITE, (950, 300, 50, 150), 2)
    throttle_label = font_small.render("Throttle", True, WHITE)
    surface.blit(throttle_label, (950, 460))

    # Brake
    brake_height = (data['brake'] / 100) * 150
    pygame.draw.rect(surface, RED, (1050, 450 - brake_height, 50, brake_height))
    pygame.draw.rect(surface, WHITE, (1050, 300, 50, 150), 2)
    brake_label = font_small.render("Brake", True, WHITE)
    surface.blit(brake_label, (1050, 460))

def draw_soc(surface, data):
    """Draws the SOC bar and power reading."""
    font_medium = pygame.font.Font(None, 50)
    font_small = pygame.font.Font(None, 30)

    # SOC Label
    soc_label = font_medium.render("SOC", True, WHITE)
    surface.blit(soc_label, (640 - soc_label.get_width() // 2, 550))

    # SOC Bar
    soc_width = (data['soc'] / 100) * 300
    soc_color = RED
    if data['soc'] > 75:
        soc_color = BLUE
    elif data['soc'] > 50:
        soc_color = GREEN
    elif data['soc'] > 25:
        soc_color = YELLOW
    pygame.draw.rect(surface, soc_color, (640 - 150, 605, soc_width, 30))
    pygame.draw.rect(surface, WHITE, (640 - 150, 605, 300, 30), 2)
    power_text = font_small.render(f"{data['power']:.1f}kW", True, WHITE)
    surface.blit(power_text, (640 + 160, 605))

def draw_lap_times(surface, data):
    """Draws the lap times."""
    font_small = pygame.font.Font(None, 30)

    # Lap Times Labels
    lap_title = font_small.render("Melhor volta", True, GREEN)
    surface.blit(lap_title, (950, 550))
    lap_prev_title = font_small.render("Volta Anterior", True, WHITE)
    surface.blit(lap_prev_title, (950, 600))
    lap_curr_title = font_small.render("Volta Atual", True, BLUE)
    surface.blit(lap_curr_title, (950, 650))

    # Lap Times
    best_lap = font_small.render(data['lap_times']['best'], True, GREEN)
    surface.blit(best_lap, (1100, 550))
    prev_lap = font_small.render(data['lap_times']['previous'], True, WHITE)
    surface.blit(prev_lap, (1100, 600))
    curr_lap = font_small.render(data['lap_times']['current'], True, BLUE)
    surface.blit(curr_lap, (1100, 650))

def draw_car_placeholder(surface, x, y, width, height, data):
    """Draws a simple rectangle as a placeholder for the car diagram."""
    # NOTE: A custom font was not downloadable, using default.
    pygame.draw.rect(surface, LIGHT_GRAY, (x, y, width, height), 2)
    font = pygame.font.Font(None, 36)
    text = font.render("Car Diagram", True, LIGHT_GRAY)
    text_rect = text.get_rect(center=(x + width / 2, y + height / 2))
    surface.blit(text, text_rect)


# --- Main Application ---
def main():
    """Main Pygame application loop."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Formula SAE Dashboard")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        data = get_simulated_data()
        screen.fill(BLACK)

        draw_separators(screen)
        draw_rpm_speed(screen, data)
        draw_tire_data(screen, data)
        draw_temp_gauges(screen, data)
        draw_status_box(screen, data)
        draw_throttle_brake_bars(screen, data)
        draw_soc(screen, data)
        draw_lap_times(screen, data)
        draw_car_placeholder(screen, 20, 100, 310, 400, data)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == '__main__':
    main()