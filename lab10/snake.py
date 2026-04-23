import random
import sys
import pygame

pygame.init()

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 22
INFO_BAR_HEIGHT = 60
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + INFO_BAR_HEIGHT

# walls
INNER_WALLS = {
    *((x, 6) for x in range(5, 12)),
    *((x, 14) for x in range(18, 26)),
    *((14, y) for y in range(8, 14)),
}

black = (0, 0, 0)
white = (255, 255, 255)
green = (50, 180, 70)
dark_green = (20, 120, 40)
red = (220, 60, 60)
gray = (70, 70, 70)
bg = (230, 235, 230)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

# fonts
font = pygame.font.SysFont("Arial", 26)
font_big = pygame.font.SysFont("Arial", 52, bold=True)


class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = [(5, 10), (4, 10), (3, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.level = 1
        self.foods_eaten = 0
        self.speed = 6
        self.food = self.generate_food_position()
        self.game_over = False

    def generate_food_position(self):
        available = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                position = (x, y)
                if position in self.snake:
                    continue
                if position in INNER_WALLS:
                    continue
                if x == 0 or y == 0 or x == GRID_WIDTH - 1 or y == GRID_HEIGHT - 1:
                    continue
                available.append(position)
        return random.choice(available)

    def change_direction(self, new_direction):
        if (new_direction[0] == -self.direction[0] and
                new_direction[1] == -self.direction[1]):
            return
        self.next_direction = new_direction

    def step(self):
        if self.game_over:
            return

        # head move
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # border collision
        x, y = new_head
        if x < 0 or y < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            self.game_over = True
            return
        if x == 0 or y == 0 or x == GRID_WIDTH - 1 or y == GRID_HEIGHT - 1:
            self.game_over = True
            return

        # inner walls collision
        if new_head in INNER_WALLS:
            self.game_over = True
            return

        # snake body collision
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.foods_eaten += 1
            self.food = self.generate_food_position()

            # level up every 4 foods.
            new_level = 1 + self.foods_eaten // 4
            if new_level > self.level:
                self.level = new_level
                self.speed += 2
        else:
            self.snake.pop()

    def draw(self):
        screen.fill(bg)

        pygame.draw.rect(screen, white, (0, 0, SCREEN_WIDTH, INFO_BAR_HEIGHT))
        pygame.draw.line(screen, gray, (0, INFO_BAR_HEIGHT), (SCREEN_WIDTH, INFO_BAR_HEIGHT), 2)

        score_text = font.render(f"Score: {self.score}", True, black)
        level_text = font.render(f"Level: {self.level}", True, black)
        speed_text = font.render(f"Speed: {self.speed}", True, black)
        
        screen.blit(score_text, (16, 16))
        screen.blit(level_text, (200, 16))
        screen.blit(speed_text, (350, 16))

        # outer border walls
        for x in range(GRID_WIDTH):
            self.draw_cell((x, 0), gray)
            self.draw_cell((x, GRID_HEIGHT - 1), gray)
        for y in range(GRID_HEIGHT):
            self.draw_cell((0, y), gray)
            self.draw_cell((GRID_WIDTH - 1, y), gray)

        # inner walls
        for wall in INNER_WALLS:
            self.draw_cell(wall, gray)

        # food
        self.draw_cell(self.food, red, inset=4)

        # snake head and body
        for index, segment in enumerate(self.snake):
            color = dark_green if index == 0 else green
            self.draw_cell(segment, color, inset=0)

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            title = font_big.render("Game Over", True, white)
            hint = font.render("Press R to restart or Esc to quit", True, white)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25)))
            screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))

    @staticmethod
    def draw_cell(cell_position, color, inset=0):
        x, y = cell_position
        rect = pygame.Rect(
            x * CELL_SIZE + inset,
            INFO_BAR_HEIGHT + y * CELL_SIZE + inset,
            CELL_SIZE - 2 * inset,
            CELL_SIZE - 2 * inset,
        )
        pygame.draw.rect(screen, color, rect)


def main():
    game = SnakeGame()

    MOVE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_EVENT, int(1000 / game.speed))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_r and game.game_over:
                    game.reset()
                    pygame.time.set_timer(MOVE_EVENT, int(1000 / game.speed))

                elif event.key in (pygame.K_UP, pygame.K_w):
                    game.change_direction((0, -1))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    game.change_direction((0, 1))
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    game.change_direction((-1, 0))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    game.change_direction((1, 0))

            if event.type == MOVE_EVENT:
                old_speed = game.speed
                game.step()
                
                if game.speed != old_speed:
                    pygame.time.set_timer(MOVE_EVENT, int(1000 / game.speed))

        game.draw()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()