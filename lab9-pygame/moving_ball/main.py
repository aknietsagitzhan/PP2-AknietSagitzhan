import pygame
from ball import Ball

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
RED = (255, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Moving Ball Game")

clock = pygame.time.Clock()

ball = Ball(
    x=SCREEN_WIDTH // 2,
    y=SCREEN_HEIGHT // 2,
    radius=25,
    color=RED,
    screen_width=SCREEN_WIDTH,
    screen_height=SCREEN_HEIGHT
)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ball.move_up()
            elif event.key == pygame.K_DOWN:
                ball.move_down()
            elif event.key == pygame.K_LEFT:
                ball.move_left()
            elif event.key == pygame.K_RIGHT:
                ball.move_right()

    screen.fill(WHITE)
    ball.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()