import pygame, sys
from pygame.locals import *
import random, time

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1) 

crash_sound = pygame.mixer.Sound("crash.wav")

# -----------------------------
# Game settings
# -----------------------------
FPS = 60
FramePerSec = pygame.time.Clock()

# colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COINS_COLLECTED = 0

# fonts
font_big = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)

game_over = font_big.render("Game Over", True, black)

background = pygame.image.load("AnimatedStreet.png")

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game")

# enemy cars
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0,int(SPEED))
        if (self.rect.bottom > SCREEN_HEIGHT):
            SCORE += 1
            self.rect.top = 0
            self.rect.centerx = random.randint(40, SCREEN_WIDTH - 40)

# player car
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        # move left
        if pressed_keys[K_LEFT] and self.rect.left > 0:
                self.rect.move_ip(-5, 0)
        # move right
        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
                self.rect.move_ip(5, 0)

# coin
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Coin.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-300, -50))

    def move(self):
        self.rect.move_ip(0, int(SPEED))
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


P1 = Player()
E1 = Enemy()

enemies = pygame.sprite.Group()
enemies.add(E1)
coins = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)

INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 2000)

# -----------------------------
# Main game loop
# -----------------------------
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == SPAWN_COIN:
            new_coin = Coin()
            coins.add(new_coin)
            all_sprites.add(new_coin)

    DISPLAYSURF.blit(background, (0, 0))
    score_text = font_small.render("SCORE: " + str(SCORE), True, black)
    DISPLAYSURF.blit(score_text, (10, 10))

    coin_text = font_small.render("COINS: " + str(COINS_COLLECTED), True, black)
    text_rect = coin_text.get_rect(topright=(SCREEN_WIDTH -10, 10))
    DISPLAYSURF.blit(coin_text, text_rect)

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.music.stop()
        crash_sound.play()
        pygame.time.delay(500)

        DISPLAYSURF.fill(red)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()

        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    collected = pygame.sprite.spritecollide(P1, coins, True)
    if collected:
        COINS_COLLECTED += len(collected)
        
    pygame.display.update()
    FramePerSec.tick(FPS)