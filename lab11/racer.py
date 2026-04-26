import pygame
import sys
import random
import time
from pygame.locals import *

# =========================================================
# Racer Game - Extended Version
# Extra features:
# 1. Random coins with different weights/values
# 2. Enemy speed increases after collecting N coins
# 3. More creative UI design
# 4. Code comments added
# =========================================================

pygame.init()
pygame.mixer.init()

# -----------------------------
# Sound setup
# -----------------------------
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)

crash_sound = pygame.mixer.Sound("crash.wav")

# Optional coin sound. If you do not have this file, remove these 2 lines.
# coin_sound = pygame.mixer.Sound("coin.wav")

# -----------------------------
# Game settings
# -----------------------------
FPS = 60
FramePerSec = pygame.time.Clock()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Main game speed values
SPEED = 5
PLAYER_SPEED = 6
SCORE = 0
COINS_COLLECTED = 0
COIN_POINTS = 0

# Enemy speed increases every N collected coins
COINS_TO_INCREASE_SPEED = 5
SPEED_INCREASE_AMOUNT = 1
MAX_SPEED = 14

# -----------------------------
# Colors
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 30, 50)
GOLD = (255, 215, 0)
SILVER = (190, 190, 190)
PURPLE = (150, 80, 255)
DARK_BLUE = (15, 20, 45)
NEON_BLUE = (40, 210, 255)
NEON_GREEN = (60, 255, 140)
ORANGE = (255, 145, 40)

# -----------------------------
# Fonts
# -----------------------------
font_big = pygame.font.SysFont("Verdana", 52, bold=True)
font_medium = pygame.font.SysFont("Verdana", 24, bold=True)
font_small = pygame.font.SysFont("Verdana", 18)

# -----------------------------
# Display setup
# -----------------------------
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Creative Racer Game")

background = pygame.image.load("AnimatedStreet.png")

# -----------------------------
# Helper functions
# -----------------------------
def draw_text(surface, text, font, color, x, y):
    """Draw text on the screen."""
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_hud():
    """Draw a creative top HUD panel with score, coins, points, and speed."""
    # Semi-creative dark panel
    pygame.draw.rect(DISPLAYSURF, DARK_BLUE, (0, 0, SCREEN_WIDTH, 70))
    pygame.draw.line(DISPLAYSURF, NEON_BLUE, (0, 70), (SCREEN_WIDTH, 70), 3)

    # HUD texts
    draw_text(DISPLAYSURF, f"Score: {SCORE}", font_small, WHITE, 10, 10)
    draw_text(DISPLAYSURF, f"Coins: {COINS_COLLECTED}", font_small, GOLD, 10, 35)
    draw_text(DISPLAYSURF, f"Points: {COIN_POINTS}", font_small, NEON_GREEN, 210, 10)
    draw_text(DISPLAYSURF, f"Speed: {int(SPEED)}", font_small, ORANGE, 210, 35)


def show_game_over():
    """Show game over screen and close the game."""
    pygame.mixer.music.stop()
    crash_sound.play()
    pygame.time.delay(500)

    DISPLAYSURF.fill(RED)

    game_over_text = font_big.render("Game Over", True, BLACK)
    final_score_text = font_medium.render(f"Final Score: {SCORE}", True, WHITE)
    final_coin_text = font_medium.render(f"Coins: {COINS_COLLECTED}", True, GOLD)
    final_points_text = font_medium.render(f"Coin Points: {COIN_POINTS}", True, NEON_GREEN)

    DISPLAYSURF.blit(game_over_text, (35, 190))
    DISPLAYSURF.blit(final_score_text, (95, 280))
    DISPLAYSURF.blit(final_coin_text, (125, 320))
    DISPLAYSURF.blit(final_points_text, (85, 360))

    pygame.display.update()
    time.sleep(2)
    pygame.quit()
    sys.exit()


# -----------------------------
# Enemy car class
# -----------------------------
class Enemy(pygame.sprite.Sprite):
    """Enemy car that moves down the road."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        """Place enemy back at the top with random x-position."""
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -50)

    def move(self):
        """Move enemy down. Increase score when it passes the player."""
        global SCORE
        self.rect.move_ip(0, int(SPEED))

        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset_position()


# -----------------------------
# Player car class
# -----------------------------
class Player(pygame.sprite.Sprite):
    """Player car controlled with arrow keys."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, 520)

    def move(self):
        """Move player left and right."""
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-PLAYER_SPEED, 0)

        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(PLAYER_SPEED, 0)


# -----------------------------
# Coin class
# -----------------------------
class Coin(pygame.sprite.Sprite):
    """
    Coin with random weight/value.
    Different weights give different points and different colors.
    """

    def __init__(self):
        super().__init__()

        # Randomly choose coin type.
        # value = how many points the coin gives.
        # size = coin radius.
        # color = coin color.
        coin_types = [
            {"value": 1, "size": 10, "color": GOLD, "name": "Bronze"},
            {"value": 2, "size": 13, "color": SILVER, "name": "Silver"},
            {"value": 3, "size": 16, "color": PURPLE, "name": "Diamond"},
        ]

        # Use weighted random choice.
        # Small coins appear often, big coins appear rarely.
        self.coin_type = random.choices(
            coin_types,
            weights=[60, 30, 10],
            k=1
        )[0]

        self.value = self.coin_type["value"]
        self.radius = self.coin_type["size"]
        self.color = self.coin_type["color"]
        self.name = self.coin_type["name"]

        # Create a simple coin design using circles instead of only an image.
        self.image = pygame.Surface((self.radius * 2 + 8, self.radius * 2 + 8), pygame.SRCALPHA)
        center = (self.radius + 4, self.radius + 4)

        # Outer glow
        pygame.draw.circle(self.image, (255, 255, 255, 80), center, self.radius + 4)
        # Main coin body
        pygame.draw.circle(self.image, self.color, center, self.radius)
        # Dark outline
        pygame.draw.circle(self.image, BLACK, center, self.radius, 2)
        # Inner shine
        pygame.draw.circle(self.image, WHITE, (center[0] - 4, center[1] - 4), max(3, self.radius // 4))

        self.rect = self.image.get_rect()
        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(-350, -60)
        )

    def move(self):
        """Move coin down. Delete it when it leaves the screen."""
        self.rect.move_ip(0, int(SPEED))

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# -----------------------------
# Create sprites
# -----------------------------
P1 = Player()
E1 = Enemy()

enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)

# -----------------------------
# Custom events
# -----------------------------
# Coin spawn event: creates a new coin every 1.2 seconds
SPAWN_COIN = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_COIN, 1200)

# -----------------------------
# Main game loop
# -----------------------------
while True:
    # -----------------------------
    # Event handling
    # -----------------------------
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Create new random coin
        if event.type == SPAWN_COIN:
            new_coin = Coin()
            coins.add(new_coin)
            all_sprites.add(new_coin)

    # -----------------------------
    # Draw background and HUD
    # -----------------------------
    DISPLAYSURF.blit(background, (0, 0))
    draw_hud()

    # -----------------------------
    # Draw and move all sprites
    # -----------------------------
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # -----------------------------
    # Check collision between player and enemy
    # -----------------------------
    if pygame.sprite.spritecollideany(P1, enemies):
        for entity in all_sprites:
            entity.kill()
        show_game_over()

    # -----------------------------
    # Check collision between player and coins
    # -----------------------------
    collected_coins = pygame.sprite.spritecollide(P1, coins, True)

    for coin in collected_coins:
        COINS_COLLECTED += 1
        COIN_POINTS += coin.value

        # Optional sound if you have coin.wav
        # coin_sound.play()

        # Increase enemy speed after every N coins collected
        if COINS_COLLECTED % COINS_TO_INCREASE_SPEED == 0:
            SPEED = min(SPEED + SPEED_INCREASE_AMOUNT, MAX_SPEED)

    # -----------------------------
    # Update display
    # -----------------------------
    pygame.display.update()
    FramePerSec.tick(FPS)
