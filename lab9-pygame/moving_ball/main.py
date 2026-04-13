import pygame
from ball import Ball

pygame.init()

WHITE = (255, 255, 255)
RED = (255, 0, 0)

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Moving Ball Game")

clock = pygame.time.Clock()

ball = Ball(
    x=800 // 2,
    y=600 // 2,
    radius=25,
    color=RED,
    screen_width=800,
    screen_height=600
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