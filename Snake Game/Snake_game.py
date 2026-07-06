import pygame
import random

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
EASY_SPEED = 10
NORMAL_SPEED = 15
HARD_SPEED = 20

# Obstacle and food settings
REVERSE_OBSTACLE = "reverse"
DEADLY_OBSTACLE = "deadly"
FOOD_TYPES = {
    "normal": {"color": RED, "length_gain": 1},
    "bonus": {"color": YELLOW, "length_gain": 2},
    "poison": {"color": PURPLE, "length_gain": 0},
}

# Font settings
font = pygame.font.SysFont("comicsans", 25)
clock = pygame.time.Clock()


def draw_text(text, color, x, y, bg_color=None):
    shadow_color = (8, 8, 8)
    shadow_msg = font.render(text, True, shadow_color, bg_color)
    screen.blit(shadow_msg, [x + 2, y + 2])
    msg = font.render(text, True, color, bg_color)
    screen.blit(msg, [x, y])


def start_menu():
    while True:
        screen.fill(BLACK)
        pygame.draw.rect(screen, BLUE, [0, 0, WIDTH, HEIGHT // 3])
        pygame.draw.rect(screen, PURPLE, [0, HEIGHT // 3, WIDTH, HEIGHT // 3])
        pygame.draw.rect(screen, CYAN, [0, 2 * HEIGHT // 3, WIDTH, HEIGHT // 3])

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


def message(text, color):
    draw_text(text, color, WIDTH / 6, HEIGHT / 3)


def spawn_obstacles(snake_list):
    obstacles = []
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


def spawn_food(snake_list, obstacles):
    blocked_positions = {(segment[0], segment[1]) for segment in snake_list}
    blocked_positions.update((obstacle["x"], obstacle["y"]) for obstacle in obstacles)

    while True:
        x = round(random.randrange(0, WIDTH - SNAKE_SIZE) / 20.0) * 20.0
        y = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / 20.0) * 20.0
        if (x, y) in blocked_positions:
            continue

        food_type = random.choices(list(FOOD_TYPES.keys()), weights=[0.7, 0.2, 0.1])[0]
        return x, y, food_type


def apply_obstacle_effect(x_change, y_change, obstacle):
    if obstacle["kind"] == REVERSE_OBSTACLE:
        return -x_change, -y_change, False
    return x_change, y_change, True


def draw_obstacles(obstacles):
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
    obstacles = spawn_obstacles(snake_list)
    foodx, foody, food_type = spawn_food(snake_list, obstacles)

    while not game_over:
        while game_close:
            screen.fill(BLACK)
            message("You lost! Press Q-Quit or C-Play Again", RED)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        return False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
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

        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        x += x_change
        y += y_change

        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        screen.fill(BLACK)
        draw_obstacles(obstacles)
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
                if hit_deadly:
                    game_close = True
                break

        draw_snake(snake_list)

        draw_text("Score: " + str(length_of_snake - 1), WHITE, 5, 5)
        pygame.display.update()

        if x == foodx and y == foody:
            if food_type == "poison":
                game_close = True
            else:
                gain = FOOD_TYPES[food_type]["length_gain"]
                foodx, foody, food_type = spawn_food(snake_list, obstacles)
                length_of_snake += gain

        clock.tick(snake_speed)


if __name__ == "__main__":
    while True:
        selected_speed = start_menu()
        should_quit = game(selected_speed)
        if should_quit:
            break
    pygame.quit()