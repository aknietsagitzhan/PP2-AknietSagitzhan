import os
import pygame
from player import MusicPlayer

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Music Player")

clock = pygame.time.Clock()

music_folder = os.path.join(os.path.dirname(__file__), "music")
player = MusicPlayer(music_folder)

# Colors
BG_COLOR = (18, 18, 18)
PANEL_COLOR = (35, 35, 35)
TITLE_COLOR = (227, 84, 235)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (245, 66, 78)
BAR_BG = (70, 70, 70)
BAR_FILL = (0, 200, 255)

# Fonts
title_font = pygame.font.Font(None, 60)
text_font = pygame.font.Font(None, 34)
small_font = pygame.font.Font(None, 28)

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

    # Background
    screen.fill(BG_COLOR)

    # Main panel
    panel_rect = pygame.Rect(110, 50, 700, 410)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=30)

    # Title
    title_surface = title_font.render("Akniet's Music Player", True, TITLE_COLOR)
    screen.blit(title_surface, (240, 90))

    # Track name
    track_name = player.get_current_track_name()
    track_surface = text_font.render(f"Track: {track_name}", True, TEXT_COLOR)
    screen.blit(track_surface, (150, 190))

    # Status
    status = "Playing" if player.is_playing else "Stopped"
    status_surface = text_font.render(f"Status: {status}", True, ACCENT_COLOR)
    screen.blit(status_surface, (150, 240))

    # Position
    position = player.get_position_seconds()
    position_surface = text_font.render(f"Position: {position} sec", True, TEXT_COLOR)
    screen.blit(position_surface, (150, 290))

    #Progress bar based on seconds
    progress_width = min(position * 10, 600)
    pygame.draw.rect(screen, BAR_BG, (150, 340, 600, 10), border_radius=10)
    pygame.draw.rect(screen, BAR_FILL, (150, 340, progress_width, 10), border_radius=10)

    # Controls
    controls1 = small_font.render("P = Play   S = Stop   N = Next", True, TEXT_COLOR)
    controls2 = small_font.render("B = Previous   Q = Quit", True, TEXT_COLOR)
    screen.blit(controls1, (150, 380))
    screen.blit(controls2, (150, 410))

    pygame.display.flip()
    clock.tick(30)

pygame.mixer.music.stop()
pygame.quit()