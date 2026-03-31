import os
import pygame
from player import MusicPlayer


pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 200)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Music Player")

font_title = pygame.font.Font(None, 48)
font_text = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 28)

clock = pygame.time.Clock()

music_folder = os.path.join(os.path.dirname(__file__), "music")
player = MusicPlayer(music_folder)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next_track()
            elif event.key == pygame.K_b:
                player.previous_track()
            elif event.key == pygame.K_q:
                running = False

    screen.fill(WHITE)

    title_surface = font_title.render("Music Player", True, BLUE)
    track_surface = font_text.render(
        f"Current Track: {player.get_current_track_name()}", True, BLACK
    )

    status_text = "Playing" if player.is_playing else "Stopped"
    status_surface = font_text.render(f"Status: {status_text}", True, BLACK)

    position_surface = font_text.render(
        f"Position: {player.get_position_seconds()} sec",
        True,
        BLACK
    )

    controls_surface1 = font_small.render("P = Play   S = Stop   N = Next", True, BLACK)
    controls_surface2 = font_small.render("B = Previous   Q = Quit", True, BLACK)

    screen.blit(title_surface, (280, 40))
    screen.blit(track_surface, (80, 130))
    screen.blit(status_surface, (80, 180))
    screen.blit(position_surface, (80, 230))
    screen.blit(controls_surface1, (80, 300))
    screen.blit(controls_surface2, (80, 335))

    pygame.display.flip()
    clock.tick(30)

pygame.mixer.music.stop()
pygame.quit()