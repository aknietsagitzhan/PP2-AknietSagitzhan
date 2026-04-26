import random
import sys
import pygame

# =========================================================
# Snake Game - Extended Version
# Extra features:
# 1. Randomly generated food with different weights/values
# 2. Food disappears after some time using a timer
# 3. Commented code
# =========================================================

pygame.init()

# -----------------------------
# Grid and screen settings
# -----------------------------
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 22
INFO_BAR_HEIGHT = 70
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + INFO_BAR_HEIGHT

# -----------------------------
# Inner wall positions
# -----------------------------
INNER_WALLS = {
    *((x, 6) for x in range(5, 12)),
    *((x, 14) for x in range(18, 26)),
    *((14, y) for y in range(8, 14)),
}

# -----------------------------
# Colors
# -----------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 180, 70)
DARK_GREEN = (20, 120, 40)
RED = (220, 60, 60)
GRAY = (70, 70, 70)
BG = (230, 235, 230)
YELLOW = (245, 210, 40)
PURPLE = (160, 80, 230)
BLUE = (70, 160, 255)
DARK_PANEL = (25, 35, 45)
ORANGE = (255, 150, 50)

# -----------------------------
# Pygame setup
# -----------------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake - Weighted Food")
clock = pygame.time.Clock()

# -----------------------------
# Fonts
# -----------------------------
font = pygame.font.SysFont("Arial", 24)
font_small = pygame.font.SysFont("Arial", 18)
font_big = pygame.font.SysFont("Arial", 52, bold=True)


class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all game variables to start a new game."""
        self.snake = [(5, 10), (4, 10), (3, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.score = 0
        self.level = 1
        self.foods_eaten = 0
        self.speed = 6
        self.game_over = False

        # Create the first food with random type and timer.
        self.food = self.generate_food()

    def generate_food_position(self):
        """Generate a random empty cell for food."""
        available = []

        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                position = (x, y)

                # Food must not appear on snake body.
                if position in self.snake:
                    continue

                # Food must not appear on inner walls.
                if position in INNER_WALLS:
                    continue

                # Food must not appear on border walls.
                if x == 0 or y == 0 or x == GRID_WIDTH - 1 or y == GRID_HEIGHT - 1:
                    continue

                available.append(position)

        return random.choice(available)

    def generate_food(self):
        """
        Generate food with different weights.
        Weight means how often each food type appears.
        Bigger value food appears less often.
        """
        food_types = [
            {
                "name": "Apple",
                "value": 10,
                "color": RED,
                "radius": 7,
                "lifetime": 7000,
                "weight": 60,
            },
            {
                "name": "Banana",
                "value": 20,
                "color": YELLOW,
                "radius": 8,
                "lifetime": 5500,
                "weight": 30,
            },
            {
                "name": "Berry",
                "value": 30,
                "color": PURPLE,
                "radius": 9,
                "lifetime": 4000,
                "weight": 10,
            },
        ]

        # Pick one food type using weighted random choice.
        chosen_food = random.choices(
            food_types,
            weights=[food["weight"] for food in food_types],
            k=1,
        )[0]

        # Store food data in a dictionary.
        return {
            "position": self.generate_food_position(),
            "name": chosen_food["name"],
            "value": chosen_food["value"],
            "color": chosen_food["color"],
            "radius": chosen_food["radius"],
            "lifetime": chosen_food["lifetime"],
            "created_time": pygame.time.get_ticks(),
        }

    def get_food_time_left(self):
        """Return how many milliseconds are left before food disappears."""
        current_time = pygame.time.get_ticks()
        passed_time = current_time - self.food["created_time"]
        return max(0, self.food["lifetime"] - passed_time)

    def update_food_timer(self):
        """If food timer is finished, remove old food and generate new food."""
        if self.get_food_time_left() <= 0:
            self.food = self.generate_food()

    def change_direction(self, new_direction):
        """Change snake direction, but prevent moving backward into itself."""
        if (
            new_direction[0] == -self.direction[0]
            and new_direction[1] == -self.direction[1]
        ):
            return

        self.next_direction = new_direction

    def step(self):
        """Move the snake one cell and check collisions."""
        if self.game_over:
            return

        # Update direction.
        self.direction = self.next_direction

        # Calculate new head position.
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        x, y = new_head

        # Collision with screen border.
        if x < 0 or y < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            self.game_over = True
            return

        # Collision with border walls.
        if x == 0 or y == 0 or x == GRID_WIDTH - 1 or y == GRID_HEIGHT - 1:
            self.game_over = True
            return

        # Collision with inner walls.
        if new_head in INNER_WALLS:
            self.game_over = True
            return

        # Collision with snake body.
        if new_head in self.snake:
            self.game_over = True
            return

        # Add new head to the front of the snake.
        self.snake.insert(0, new_head)

        # Check if snake eats food.
        if new_head == self.food["position"]:
            self.score += self.food["value"]
            self.foods_eaten += 1

            # Generate new random food after eating.
            self.food = self.generate_food()

            # Level up every 4 foods.
            new_level = 1 + self.foods_eaten // 4
            if new_level > self.level:
                self.level = new_level
                self.speed += 2
        else:
            # If food is not eaten, remove tail so snake length stays same.
            self.snake.pop()

    def draw(self):
        """Draw all game objects."""
        screen.fill(BG)

        # Draw top information bar.
        pygame.draw.rect(screen, DARK_PANEL, (0, 0, SCREEN_WIDTH, INFO_BAR_HEIGHT))
        pygame.draw.line(screen, BLUE, (0, INFO_BAR_HEIGHT), (SCREEN_WIDTH, INFO_BAR_HEIGHT), 3)

        # Draw score information.
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        speed_text = font.render(f"Speed: {self.speed}", True, ORANGE)

        screen.blit(score_text, (16, 10))
        screen.blit(level_text, (190, 10))
        screen.blit(speed_text, (350, 10))

        # Draw food information and timer.
        food_name = self.food["name"]
        food_value = self.food["value"]
        time_left_seconds = self.get_food_time_left() / 1000

        food_text = font_small.render(
            f"Food: {food_name} +{food_value} | Time: {time_left_seconds:.1f}s",
            True,
            self.food["color"],
        )
        screen.blit(food_text, (16, 42))

        # Draw outer border walls.
        for x in range(GRID_WIDTH):
            self.draw_cell((x, 0), GRAY)
            self.draw_cell((x, GRID_HEIGHT - 1), GRAY)

        for y in range(GRID_HEIGHT):
            self.draw_cell((0, y), GRAY)
            self.draw_cell((GRID_WIDTH - 1, y), GRAY)

        # Draw inner walls.
        for wall in INNER_WALLS:
            self.draw_cell(wall, GRAY)

        # Draw current food.
        self.draw_food()

        # Draw snake body and head.
        for index, segment in enumerate(self.snake):
            color = DARK_GREEN if index == 0 else GREEN
            self.draw_cell(segment, color, inset=1)

        # Draw game over overlay.
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            title = font_big.render("Game Over", True, WHITE)
            hint = font.render("Press R to restart or Esc to quit", True, WHITE)

            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25)))
            screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))

    def draw_food(self):
        """Draw food as a circle with a small shine effect."""
        x, y = self.food["position"]
        center_x = x * CELL_SIZE + CELL_SIZE // 2
        center_y = INFO_BAR_HEIGHT + y * CELL_SIZE + CELL_SIZE // 2

        pygame.draw.circle(
            screen,
            self.food["color"],
            (center_x, center_y),
            self.food["radius"],
        )

        # Small shine circle for better design.
        pygame.draw.circle(
            screen,
            WHITE,
            (center_x - 3, center_y - 3),
            2,
        )

    @staticmethod
    def draw_cell(cell_position, color, inset=0):
        """Draw one grid cell."""
        x, y = cell_position

        rect = pygame.Rect(
            x * CELL_SIZE + inset,
            INFO_BAR_HEIGHT + y * CELL_SIZE + inset,
            CELL_SIZE - 2 * inset,
            CELL_SIZE - 2 * inset,
        )

        pygame.draw.rect(screen, color, rect, border_radius=4)


def main():
    """Main function that runs the game loop."""
    game = SnakeGame()

    # Snake movement event.
    MOVE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_EVENT, int(1000 / game.speed))

    while True:
        for event in pygame.event.get():
            # Quit game.
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard controls.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # Restart game after game over.
                if event.key == pygame.K_r and game.game_over:
                    game.reset()
                    pygame.time.set_timer(MOVE_EVENT, int(1000 / game.speed))

                # Snake movement controls: arrows or WASD.
                elif event.key in (pygame.K_UP, pygame.K_w):
                    game.change_direction((0, -1))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    game.change_direction((0, 1))
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    game.change_direction((-1, 0))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    game.change_direction((1, 0))

            # Move snake only when movement event happens.
            if event.type == MOVE_EVENT:
                old_speed = game.speed
                game.step()

                # If speed changed after level up, update timer speed.
                if game.speed != old_speed:
                    pygame.time.set_timer(MOVE_EVENT, int(1000 / game.speed))

        # Check food timer every frame.
        if not game.game_over:
            game.update_food_timer()

        # Draw everything.
        game.draw()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
