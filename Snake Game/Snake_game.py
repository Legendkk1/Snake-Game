import os
import math
import random
from array import array
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
WHITE = (235, 235, 235)
BLACK = (18, 18, 18)
GREEN = (70, 180, 95)
RED = (220, 80, 80)
YELLOW = (220, 190, 80)
CYAN = (90, 180, 200)
PURPLE = (150, 95, 180)
ORANGE = (220, 150, 90)
BLUE = (75, 110, 200)

# Snake settings
SNAKE_SIZE = 20
EASY_SPEED = 3
NORMAL_SPEED = 7
HARD_SPEED = 12

# Obstacle and food settings
REVERSE_OBSTACLE = "reverse"
DEADLY_OBSTACLE = "deadly"
FOOD_TYPES = {
    "normal": {"color": RED, "length_gain": 1},
    "bonus": {"color": YELLOW, "length_gain": 2},
    "poison": {"color": PURPLE, "length_gain": 0},
    "reverse": {"color": BLUE, "length_gain": 0},
}

# Font settings
font = pygame.font.SysFont("comicsans", 25)
clock = pygame.time.Clock()

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
except pygame.error:
    pygame.mixer.init = None


def make_sound(frequency, duration, volume=0.15):
    if pygame.mixer.init is None:
        return None

    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    samples = array("h")
    for i in range(num_samples):
        t = i / sample_rate
        value = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
        samples.append(value)
    return pygame.mixer.Sound(buffer=samples.tobytes())


SOUNDS = {}
if pygame.mixer.init is not None:
    SOUNDS["eat"] = make_sound(900, 0.08, 0.12)
    SOUNDS["reverse"] = make_sound(700, 0.12, 0.10)
    SOUNDS["lose"] = make_sound(220, 0.18, 0.10)
    SOUNDS["bonus"] = make_sound(1200, 0.09, 0.12)
    SOUNDS["levelup"] = make_sound(1040, 0.14, 0.08)



# Background Music
MUSIC_FILE = os.path.join(os.path.dirname(__file__), "lofi.mp3")
try:
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.set_volume(0.30)
except pygame.error:
    print("Could not load lofi.mp3")

background_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "snake.png"))
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))


def draw_background(level=1):
    screen.blit(background_image, (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    if level == 2:
        overlay.fill((15, 25, 70, 140))
        for x in range(0, WIDTH, 40):
            pygame.draw.line(screen, (50, 80, 130), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(screen, (50, 80, 130), (0, y), (WIDTH, y), 1)
    else:
        overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))


def draw_text(text, color, x, y, bg_color=None):
    shadow_color = (8, 8, 8)
    shadow_msg = font.render(text, True, shadow_color, bg_color)
    screen.blit(shadow_msg, [x + 2, y + 2])
    msg = font.render(text, True, color, bg_color)
    screen.blit(msg, [x, y])


def play_sound(name):
    sound = SOUNDS.get(name)
    if sound is not None:
        sound.play()


def start_menu():
    while True:
        draw_background()

        title_text = "Snake Game"
        easy_text = "1 - Easy (Slow)"
        normal_text = "2 - Normal"
        hard_text = "3 - Hard (Fast)"
        help_text = "Press 1, 2, or 3 to choose difficulty"
        extra_text = "E / N / H keys also work"

        draw_text(title_text, YELLOW, WIDTH / 4, HEIGHT / 8, BLACK)
        pygame.draw.line(screen, WHITE, (WIDTH / 6, HEIGHT / 4 + 30), (WIDTH * 5 / 6, HEIGHT / 4 + 30), 4)
        draw_text(easy_text, GREEN, WIDTH / 4, HEIGHT / 3 + 20, BLACK)
        draw_text(normal_text, WHITE, WIDTH / 4, HEIGHT / 3 + 70, BLACK)
        draw_text(hard_text, ORANGE, WIDTH / 4, HEIGHT / 3 + 120, BLACK)
        draw_text(help_text, WHITE, WIDTH / 6, HEIGHT / 3 + 200, BLACK)
        draw_text(extra_text, YELLOW, WIDTH / 6, HEIGHT / 3 + 240, BLACK)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.fadeout(2000)
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 or event.key == pygame.K_e:
                    return EASY_SPEED
                elif event.key == pygame.K_2 or event.key == pygame.K_n:
                    return NORMAL_SPEED
                elif event.key == pygame.K_3 or event.key == pygame.K_h:
                    return HARD_SPEED


def draw_snake(snake_list):
    for x, y in snake_list:
        pygame.draw.rect(screen, GREEN, [x, y, SNAKE_SIZE, SNAKE_SIZE])


LEVEL2_SCORE_THRESHOLD = 25


def message(text, color):
    draw_text(text, color, WIDTH / 6, HEIGHT / 3)


def get_level(score):
    return 2 if score >= LEVEL2_SCORE_THRESHOLD else 1


def create_maze_walls():
    walls = []
    for x in range(120, WIDTH - 120 + 1, SNAKE_SIZE):
        walls.append({"x": x, "y": HEIGHT // 3, "kind": "wall"})
        walls.append({"x": x, "y": HEIGHT * 2 // 3, "kind": "wall"})
    for y in range(HEIGHT // 3, HEIGHT * 2 // 3 + 1, SNAKE_SIZE):
        if y == HEIGHT // 2:
            continue
        walls.append({"x": WIDTH // 2, "y": y, "kind": "wall"})
    return walls


def spawn_obstacles(snake_list, level=1):
    obstacles = []
    if level == 2:
        return obstacles

    blocked_positions = {(segment[0], segment[1]) for segment in snake_list}

    while len(obstacles) < 6:
        x = round(random.randrange(0, WIDTH - SNAKE_SIZE) / 20.0) * 20.0
        y = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / 20.0) * 20.0

        if (x, y) in blocked_positions:
            continue
        if any(abs(x - obstacle["x"]) < SNAKE_SIZE and abs(y - obstacle["y"]) < SNAKE_SIZE for obstacle in obstacles):
            continue

        kind = random.choice([REVERSE_OBSTACLE, DEADLY_OBSTACLE])
        obstacles.append({"x": x, "y": y, "kind": kind})

    return obstacles


def spawn_food(snake_list, obstacles, walls=None):
    blocked_positions = {(segment[0], segment[1]) for segment in snake_list}
    blocked_positions.update((obstacle["x"], obstacle["y"]) for obstacle in obstacles)
    if walls is not None:
        blocked_positions.update((wall["x"], wall["y"]) for wall in walls)

    while True:
        x = round(random.randrange(0, WIDTH - SNAKE_SIZE) / 20.0) * 20.0
        y = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / 20.0) * 20.0
        if (x, y) in blocked_positions:
            continue

        food_type = random.choices(list(FOOD_TYPES.keys()), weights=[0.4, 0.15, 0.2, 0.25])[0]
        return x, y, food_type


def apply_obstacle_effect(x_change, y_change, obstacle):
    if obstacle["kind"] == REVERSE_OBSTACLE:
        return -x_change, -y_change, False
    return x_change, y_change, True


def draw_obstacles(obstacles, walls=None):
    if walls is not None:
        for wall in walls:
            pygame.draw.rect(screen, (120, 120, 150), [wall["x"], wall["y"], SNAKE_SIZE, SNAKE_SIZE])

    for obstacle in obstacles:
        color = CYAN if obstacle["kind"] == REVERSE_OBSTACLE else ORANGE
        pygame.draw.rect(screen, color, [obstacle["x"], obstacle["y"], SNAKE_SIZE, SNAKE_SIZE])

        if obstacle["kind"] == REVERSE_OBSTACLE:
            pygame.draw.line(screen, WHITE, (obstacle["x"] + 4, obstacle["y"] + 4), (obstacle["x"] + SNAKE_SIZE - 4, obstacle["y"] + SNAKE_SIZE - 4), 2)
        else:
            pygame.draw.line(screen, WHITE, (obstacle["x"] + 4, obstacle["y"] + 4), (obstacle["x"] + SNAKE_SIZE - 4, obstacle["y"] + SNAKE_SIZE - 4), 2)
            pygame.draw.line(screen, WHITE, (obstacle["x"] + SNAKE_SIZE - 4, obstacle["y"] + 4), (obstacle["x"] + 4, obstacle["y"] + SNAKE_SIZE - 4), 2)


def draw_food(foodx, foody, food_type):
    pygame.draw.rect(screen, FOOD_TYPES[food_type]["color"], [foodx, foody, SNAKE_SIZE, SNAKE_SIZE])


def game(snake_speed):
    game_over = False
    game_close = False

    x = WIDTH / 2
    y = HEIGHT / 2
    x_change = 0
    y_change = 0

    snake_list = [[x, y]]
    length_of_snake = 1
    level = get_level(0)
    walls = create_maze_walls() if level == 2 else []
    obstacles = spawn_obstacles(snake_list, level)
    foodx, foody, food_type = spawn_food(snake_list, obstacles, walls)

    game_over_sound_played = False

    while not game_over:
        while game_close:
            if not game_over_sound_played:
                play_sound("lose")
                pygame.mixer.music.pause()
                game_over_sound_played = True
            draw_background()
            message("You lost! Press Q-Quit or C-Play Again", RED)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.mixer.music.fadeout(1000)
                        return True
                    if event.key == pygame.K_c:
                        pygame.mixer.music.unpause()
                        return False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change != SNAKE_SIZE:
                    x_change = -SNAKE_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change != -SNAKE_SIZE:
                    x_change = SNAKE_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP and y_change != SNAKE_SIZE:
                    y_change = -SNAKE_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change != -SNAKE_SIZE:
                    y_change = SNAKE_SIZE
                    x_change = 0

        x += x_change
        y += y_change

        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        score = length_of_snake - 1
        new_level = get_level(score)
        if new_level != level:
            level = new_level
            walls = create_maze_walls() if level == 2 else []
            obstacles = spawn_obstacles(snake_list, level)
            play_sound("levelup")

        draw_background(level)
        draw_obstacles(obstacles, walls)
        draw_food(foodx, foody, food_type)

        snake_head = [x, y]
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        for obstacle in obstacles:
            if snake_head[0] == obstacle["x"] and snake_head[1] == obstacle["y"]:
                x_change, y_change, hit_deadly = apply_obstacle_effect(x_change, y_change, obstacle)
                if obstacle["kind"] == REVERSE_OBSTACLE:
                    play_sound("reverse")
                elif hit_deadly:
                    play_sound("lose")
                    game_close = True
                break

        for wall in walls:
            if snake_head[0] == wall["x"] and snake_head[1] == wall["y"]:
                play_sound("lose")
                game_close = True
                break

        draw_snake(snake_list)

        draw_text("Score: " + str(length_of_snake - 1), WHITE, 5, 5)
        pygame.display.update()
        clock.tick(snake_speed)

        if x == foodx and y == foody:
            if food_type == "poison":
                play_sound("lose")
                game_close = True
            elif food_type == "reverse":
                play_sound("reverse")
                if x_change != 0:
                    x_change = -x_change
                elif y_change != 0:
                    y_change = -y_change
                foodx, foody, food_type = spawn_food(snake_list, obstacles, walls)
            else:
                if food_type == "bonus":
                    play_sound("bonus")
                else:
                    play_sound("eat")
                gain = FOOD_TYPES[food_type]["length_gain"]
                foodx, foody, food_type = spawn_food(snake_list, obstacles, walls)
                length_of_snake += gain
    return True


if __name__ == "__main__":
    pygame.mixer.music.play(-1, fade_ms=2000)
    while True:
        selected_speed = start_menu()
        should_quit = game(selected_speed)
        if should_quit:
            break
    pygame.mixer.music.fadeout(2000)
    pygame.quit()