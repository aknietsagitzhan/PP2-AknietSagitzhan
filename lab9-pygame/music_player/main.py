import os
import pygame
from player import MusicPlayer

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((900, 500))
pygame.display.set_caption("Music Player")

clock = pygame.time.Clock()

music_folder = os.path.join(os.path.dirname(__file__), "music")
player = MusicPlayer(music_folder)

bg_c = (18, 18, 18)
panel_c = (35, 35, 35)
title_c = (227, 84, 235)
text_c = (240, 240, 240)
accent_c = (245, 66, 78)
bar_bg_c = (70, 70, 70)
bar_fill_c = (0, 200, 255)

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

    screen.fill(bg_c)

    panel_rect = pygame.Rect(110, 50, 700, 410)
    pygame.draw.rect(screen, panel_c, panel_rect, border_radius=30)

    title_surface = title_font.render("Akniet's Music Player", True, title_c)
    screen.blit(title_surface, (240, 90))

    track_name = player.get_current_track_name()
    track_surface = text_font.render(f"Track: {track_name}", True, text_c)
    screen.blit(track_surface, (150, 190))

    status = "Playing" if player.is_playing else "Stopped"
    status_surface = text_font.render(f"Status: {status}", True, accent_c)
    screen.blit(status_surface, (150, 240))

    position = player.get_position_seconds()
    position_surface = text_font.render(f"Position: {position} sec", True, text_c)
    screen.blit(position_surface, (150, 290))

    progress_width = min(position * 10, 600)
    pygame.draw.rect(screen, bar_bg_c, (150, 340, 600, 10), border_radius=10)
    pygame.draw.rect(screen, bar_fill_c, (150, 340, progress_width, 10), border_radius=10)

    controls1 = small_font.render("P = Play   S = Stop   N = Next", True, text_c)
    controls2 = small_font.render("B = Previous   Q = Quit", True, text_c)
    screen.blit(controls1, (150, 380))
    screen.blit(controls2, (150, 410))

    pygame.display.flip()
    clock.tick(30)

pygame.mixer.music.stop()
pygame.quit()