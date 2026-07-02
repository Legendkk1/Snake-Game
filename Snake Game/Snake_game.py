import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (180, 0, 255)
ORANGE = (255, 165, 0)
BLUE = (0, 120, 255)

# Snake settings
SNAKE_SIZE = 20
EASY_SPEED = 10
NORMAL_SPEED = 15
HARD_SPEED = 20

# Font settings
font = pygame.font.SysFont("comicsans", 25)
clock = pygame.time.Clock()


def draw_text(text, color, x, y, bg_color=None):
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
    msg = font.render(text, True, color)
    screen.blit(msg, [WIDTH / 6, HEIGHT / 3])


def game(snake_speed):
    game_over = False
    game_close = False

    x = WIDTH / 2
    y = HEIGHT / 2
    x_change = 0
    y_change = 0

    snake_list = [[x, y]]
    length_of_snake = 1

    foodx = round(random.randrange(0, WIDTH - SNAKE_SIZE) / 20.0) * 20.0
    foody = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / 20.0) * 20.0

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
        pygame.draw.rect(screen, RED, [foodx, foody, SNAKE_SIZE, SNAKE_SIZE])
        snake_head = [x, y]
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        draw_snake(snake_list)

        score_text = font.render("Score: " + str(length_of_snake - 1), True, WHITE)
        screen.blit(score_text, [0, 0])
        pygame.display.update()

        if x == foodx and y == foody:
            foodx = round(random.randrange(0, WIDTH - SNAKE_SIZE) / 20.0) * 20.0
            foody = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / 20.0) * 20.0
            length_of_snake += 1

        clock.tick(snake_speed)


if __name__ == "__main__":
    while True:
        selected_speed = start_menu()
        should_quit = game(selected_speed)
        if should_quit:
            break
    pygame.quit()