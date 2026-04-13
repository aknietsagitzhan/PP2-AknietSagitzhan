import os
import pygame
from clock import MickeyClock

pygame.init()

screen = pygame.display.set_mode((700, 700))
pygame.display.set_caption("Mickey Clock")

fps_clock = pygame.time.Clock()

center = (700 // 2, 700 // 2)
base_path = os.path.dirname(__file__)
clock_img = os.path.join(base_path, "images", "mickeyclock.png")

mickey_clock = MickeyClock(center, clock_img, (700, 700))

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