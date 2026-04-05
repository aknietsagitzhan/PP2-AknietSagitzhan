import os
import pygame
from clock import MickeyClock

pygame.init()

WIDTH = 700
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

fps_clock = pygame.time.Clock()

center = (WIDTH // 2, HEIGHT // 2)
base_path = os.path.dirname(__file__)

clock_img = os.path.join(base_path, "images", "mickey_h.png")

mickey_clock = MickeyClock(center, clock_img)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((245, 245, 245))
    mickey_clock.draw(screen)

    pygame.display.flip()
    fps_clock.tick(60)

pygame.quit()