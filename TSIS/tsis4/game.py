import pygame
import random
import json
import sys
import os

from config import *
from db import save_result, get_top_10, get_personal_best


class SnakeGame:
    def __init__(self):
        pygame.init()

        try:
            pygame.mixer.init()
            self.audio_available = True
        except pygame.error:
            self.audio_available = False

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.big_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.message_font = pygame.font.SysFont("Arial", 28, bold=True)

        self.settings = self.load_settings()

        self.username = ""
        self.personal_best = 0

        self.state = "menu"
        self.final_score = 0
        self.final_level = 1

        self.sounds = {}
        self.load_sounds()

        self.sprites = {}
        self.load_sprites()

        self.message_text = ""
        self.message_until = 0

        self.reset_game()

    # ---------------- SETTINGS ----------------
    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4)
            return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)

    # ---------------- ASSETS ----------------
    def load_image(self, filename):
        path = os.path.join("assets", "images", filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (CELL, CELL))
            except pygame.error:
                return None
        return None

    def load_sprites(self):
        self.sprites["apple"] = self.load_image("apple.png")

        self.sprites["head_up"] = self.load_image("head_up.png")
        self.sprites["head_down"] = self.load_image("head_down.png")
        self.sprites["head_left"] = self.load_image("head_left.png")
        self.sprites["head_right"] = self.load_image("head_right.png")

        self.sprites["tail_up"] = self.load_image("tail_up.png")
        self.sprites["tail_down"] = self.load_image("tail_down.png")
        self.sprites["tail_left"] = self.load_image("tail_left.png")
        self.sprites["tail_right"] = self.load_image("tail_right.png")

        self.sprites["body_vertical"] = self.load_image("body_vertical.png")
        self.sprites["body_horizontal"] = self.load_image("body_horizontal.png")
        self.sprites["body_topleft"] = self.load_image("body_topleft.png")
        self.sprites["body_topright"] = self.load_image("body_topright.png")
        self.sprites["body_bottomleft"] = self.load_image("body_bottomleft.png")
        self.sprites["body_bottomright"] = self.load_image("body_bottomright.png")

    def load_sound_file(self, base_name):
        if not self.audio_available:
            return None

        for ext in [".wav", ".mp3", ".ogg"]:
            path = os.path.join("assets", "sounds", base_name + ext)
            if os.path.exists(path):
                try:
                    return pygame.mixer.Sound(path)
                except pygame.error:
                    continue
        return None

    def load_sounds(self):
        self.sounds["eat"] = self.load_sound_file("eat")
        self.sounds["poison"] = self.load_sound_file("poison")
        self.sounds["powerup"] = self.load_sound_file("powerup")
        self.sounds["gameover"] = self.load_sound_file("gameover")

    def play_sound(self, name):
        if self.settings.get("sound", True) and self.audio_available:
            sound = self.sounds.get(name)
            if sound is not None:
                sound.play()

    # ---------------- HELPERS ----------------
    def draw_text(self, text, x, y, color=WHITE, center=False, font=None):
        if font is None:
            font = self.font
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = (x, y)
            self.screen.blit(img, rect)
        else:
            self.screen.blit(img, (x, y))

    def draw_button(self, rect, text, color=(90, 130, 70)):
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=12)
        self.draw_text(text, rect.centerx, rect.centery, WHITE, center=True, font=self.small_font)

    def point_in_rect(self, pos, rect):
        return rect.collidepoint(pos)

    def show_message(self, text, duration_ms=1000):
        self.message_text = text
        self.message_until = pygame.time.get_ticks() + duration_ms

    def draw_top_message(self):
        now = pygame.time.get_ticks()
        if now < self.message_until and self.message_text:
            padding_x = 16
            padding_y = 10

            text_surface = self.message_font.render(self.message_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, 30))

            bg_rect = pygame.Rect(
                text_rect.x - padding_x,
                text_rect.y - padding_y,
                text_rect.width + padding_x * 2,
                text_rect.height + padding_y * 2
            )

            pygame.draw.rect(self.screen, (120, 0, 0), bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, bg_rect, 2, border_radius=10)
            self.screen.blit(text_surface, text_rect)

    def draw_grid(self):
        if not self.settings["grid"]:
            return
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(self.screen, (155, 205, 70), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(self.screen, (155, 205, 70), (0, y), (WIDTH, y))

    def draw_checker_background(self):
        c1 = (170, 215, 81)
        c2 = (162, 209, 73)

        for row in range(ROWS):
            for col in range(COLS):
                color = c1 if (row + col) % 2 == 0 else c2
                pygame.draw.rect(
                    self.screen,
                    color,
                    (col * CELL, row * CELL, CELL, CELL)
                )

    def reset_game(self):
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.prev_snake = self.snake[:]
        self.render_snake = self.snake[:]

        self.dx, self.dy = 1, 0

        self.score = 0
        self.level = 1
        self.food_eaten = 0

        self.base_speed = BASE_SNAKE_SPEED
        self.current_speed = self.base_speed
        self.max_speed = 12
        self.move_delay = 1000 / self.current_speed
        self.last_move_time = pygame.time.get_ticks()

        self.shield = False
        self.active_effect = None
        self.effect_end_time = 0

        self.obstacles = set()
        self.powerup = None
        self.last_powerup_spawn = pygame.time.get_ticks()

        self.food = None
        self.poison_food = None

        self.food = self.generate_food()
        self.poison_food = self.generate_poison_food()

        self.game_saved = False
        self.message_text = ""
        self.message_until = 0

    def get_occupied_positions(self, include_food=True, include_poison=True, include_powerup=True):
        occupied = set(self.snake) | set(self.obstacles)

        if include_food and self.food is not None:
            occupied.add(self.food["pos"])
        if include_poison and self.poison_food is not None:
            occupied.add(self.poison_food["pos"])
        if include_powerup and self.powerup is not None:
            occupied.add(self.powerup["pos"])

        return occupied

    def random_free_position(self):
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in self.get_occupied_positions():
                return pos

    def generate_food(self):
        food_type = random.choice(FOOD_TYPES)
        return {
            "pos": self.random_free_position(),
            "score": food_type["score"],
            "color": food_type["color"],
            "time": food_type["time"],
            "spawn_time": pygame.time.get_ticks()
        }

    def generate_poison_food(self):
        return {
            "pos": self.random_free_position(),
            "color": DARK_RED,
            "spawn_time": pygame.time.get_ticks(),
            "time": 6000
        }

    def generate_powerup(self):
        kind = random.choice(list(POWERUP_TYPES.keys()))
        data = POWERUP_TYPES[kind]
        return {
            "type": kind,
            "pos": self.random_free_position(),
            "color": data["color"],
            "spawn_time": pygame.time.get_ticks(),
            "field_time": data["field_time"]
        }

    def get_level_speed(self):
        return min(self.base_speed + (self.level - 1) * 0.5, self.max_speed)

    def apply_current_speed(self):
        self.current_speed = self.get_level_speed()

        if self.active_effect == "speed":
            self.current_speed = min(self.current_speed + 2, self.max_speed + 2)
        elif self.active_effect == "slow":
            self.current_speed = max(4, self.current_speed - 2)

        self.move_delay = 1000 / self.current_speed

    def level_up(self):
        self.level += 1
        self.apply_current_speed()

        if self.level >= 3:
            self.generate_obstacles()

    def count_free_neighbors(self, pos, obstacle_set):
        x, y = pos
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        count = 0
        for nx, ny in neighbors:
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if (nx, ny) not in obstacle_set and (nx, ny) not in self.snake:
                    count += 1
        return count

    def generate_obstacles(self):
        target_count = min(5 + self.level, 18)

        head = self.snake[0]
        safe_zone = {
            head,
            (head[0] + 1, head[1]),
            (head[0] - 1, head[1]),
            (head[0], head[1] + 1),
            (head[0], head[1] - 1),
        }

        best_obstacles = set()

        for _ in range(50):
            obstacles = set()
            attempts = 0

            while len(obstacles) < target_count and attempts < 1000:
                pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
                attempts += 1

                if pos in self.snake or pos in safe_zone:
                    continue

                obstacles.add(pos)

            if self.count_free_neighbors(head, obstacles) >= 2:
                best_obstacles = obstacles
                break

        self.obstacles = best_obstacles

        self.food = None
        self.poison_food = None
        self.powerup = None

        self.food = self.generate_food()
        self.poison_food = self.generate_poison_food()

    def activate_powerup(self, kind):
        now = pygame.time.get_ticks()

        if kind == "speed":
            self.active_effect = "speed"
            self.effect_end_time = now + POWERUP_TYPES["speed"]["duration"]
            self.apply_current_speed()

        elif kind == "slow":
            self.active_effect = "slow"
            self.effect_end_time = now + POWERUP_TYPES["slow"]["duration"]
            self.apply_current_speed()

        elif kind == "shield":
            self.shield = True
            self.active_effect = "shield"
            self.effect_end_time = 0

    def update_effects(self):
        now = pygame.time.get_ticks()

        if self.active_effect in ("speed", "slow") and now >= self.effect_end_time:
            self.active_effect = None
            self.apply_current_speed()

    def save_game_result_once(self):
        if not self.game_saved and self.username.strip():
            save_result(self.username.strip(), self.final_score, self.final_level)
            self.game_saved = True

    # ---------------- SPRITE DRAWING ----------------
    def get_head_sprite(self):
        if self.dx == 1:
            return self.sprites.get("head_right")
        if self.dx == -1:
            return self.sprites.get("head_left")
        if self.dy == -1:
            return self.sprites.get("head_up")
        return self.sprites.get("head_down")

    def get_tail_sprite_name(self, tail, before_tail):
        dx = tail[0] - before_tail[0]
        dy = tail[1] - before_tail[1]

        if dx == 1:
            return "tail_right"
        if dx == -1:
            return "tail_left"
        if dy == 1:
            return "tail_down"
        return "tail_up"

    def get_body_sprite_name_render(self, prev_part, current_part, next_part):
        d1x = prev_part[0] - current_part[0]
        d1y = prev_part[1] - current_part[1]
        d2x = next_part[0] - current_part[0]
        d2y = next_part[1] - current_part[1]

        def norm(dx, dy):
            if abs(dx) > abs(dy):
                return (1, 0) if dx > 0 else (-1, 0)
            return (0, 1) if dy > 0 else (0, -1)

        d1 = norm(d1x, d1y)
        d2 = norm(d2x, d2y)
        directions = {d1, d2}

        if directions == {(-1, 0), (1, 0)}:
            return "body_horizontal"
        if directions == {(0, -1), (0, 1)}:
            return "body_vertical"
        if directions == {(0, -1), (1, 0)}:
            return "body_topright"
        if directions == {(0, -1), (-1, 0)}:
            return "body_topleft"
        if directions == {(0, 1), (1, 0)}:
            return "body_bottomright"
        if directions == {(0, 1), (-1, 0)}:
            return "body_bottomleft"

        return "body_horizontal"

    def get_interpolated_segment_pos(self, old_pos, new_pos, alpha):
        old_x, old_y = old_pos
        new_x, new_y = new_pos

        dx = new_x - old_x
        dy = new_y - old_y

        if abs(dx) > COLS / 2:
            if dx > 0:
                old_x += COLS
            else:
                new_x += COLS

        if abs(dy) > ROWS / 2:
            if dy > 0:
                old_y += ROWS
            else:
                new_y += ROWS

        draw_x = old_x + (new_x - old_x) * alpha
        draw_y = old_y + (new_y - old_y) * alpha

        draw_x %= COLS
        draw_y %= ROWS

        return draw_x * CELL, draw_y * CELL

    def build_render_snake(self, alpha):
        render_positions = []

        for i in range(len(self.snake)):
            new_pos = self.snake[i]

            if i < len(self.prev_snake):
                old_pos = self.prev_snake[i]
            else:
                old_pos = new_pos

            px, py = self.get_interpolated_segment_pos(old_pos, new_pos, alpha)
            render_positions.append((px / CELL, py / CELL))

        self.render_snake = render_positions

    def draw_smooth_head(self, alpha):
        if not self.snake:
            return

        head_sprite = self.get_head_sprite()
        if head_sprite is None:
            return

        old_head = self.prev_snake[0] if self.prev_snake else self.snake[0]
        new_head = self.snake[0]

        pos = self.get_interpolated_segment_pos(old_head, new_head, alpha)
        self.screen.blit(head_sprite, pos)

    def draw_snake(self, alpha):
        if len(self.snake) == 1:
            self.draw_smooth_head(alpha)
            return

        self.build_render_snake(alpha)

        for i in range(1, len(self.snake) - 1):
            prev_part = self.render_snake[i - 1]
            current_part = self.render_snake[i]
            next_part = self.render_snake[i + 1]

            sprite_name = self.get_body_sprite_name_render(prev_part, current_part, next_part)
            sprite = self.sprites.get(sprite_name)

            if sprite:
                self.screen.blit(sprite, (current_part[0] * CELL, current_part[1] * CELL))

        tail = self.render_snake[-1]
        before_tail = self.render_snake[-2]

        tail_dx = tail[0] - before_tail[0]
        tail_dy = tail[1] - before_tail[1]

        if abs(tail_dx) > abs(tail_dy):
            tail_name = "tail_right" if tail_dx > 0 else "tail_left"
        else:
            tail_name = "tail_down" if tail_dy > 0 else "tail_up"

        tail_sprite = self.sprites.get(tail_name)
        if tail_sprite:
            self.screen.blit(tail_sprite, (tail[0] * CELL, tail[1] * CELL))

        self.draw_smooth_head(alpha)

    # ---------------- SCREENS ----------------
    def menu_screen(self):
        play_btn = pygame.Rect(WIDTH // 2 - 110, 200, 220, 60)
        leader_btn = pygame.Rect(WIDTH // 2 - 110, 260, 220, 60)
        settings_btn = pygame.Rect(WIDTH // 2 - 110, 320, 220, 60)
        quit_btn = pygame.Rect(WIDTH // 2 - 110, 380, 220, 60)
        username_box = pygame.Rect(WIDTH // 2 - 150, 125, 300, 50)

        while self.state == "menu":
            self.draw_checker_background()

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 35))
            self.screen.blit(overlay, (0, 0))

            self.draw_text("SNAKE", WIDTH // 2, 60, WHITE, center=True, font=self.big_font)
            self.draw_text("Enter username", WIDTH // 2, 102, WHITE, center=True, font=self.small_font)

            pygame.draw.rect(self.screen, (70, 110, 60), username_box, border_radius=12)
            pygame.draw.rect(self.screen, WHITE, username_box, 2, border_radius=12)
            self.draw_text(self.username if self.username else "type here...", username_box.x + 12, username_box.y + 9)

            self.draw_button(play_btn, "Play")
            self.draw_button(leader_btn, "Leaderboard")
            self.draw_button(settings_btn, "Settings")
            self.draw_button(quit_btn, "Quit")

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.username.strip():
                            self.personal_best = get_personal_best(self.username.strip())
                            self.reset_game()
                            self.state = "game"
                    else:
                        if len(self.username) < 15 and event.unicode.isprintable():
                            self.username += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos

                    if self.point_in_rect(pos, play_btn):
                        if self.username.strip():
                            self.personal_best = get_personal_best(self.username.strip())
                            self.reset_game()
                            self.state = "game"
                    elif self.point_in_rect(pos, leader_btn):
                        self.state = "leaderboard"
                    elif self.point_in_rect(pos, settings_btn):
                        self.state = "settings"
                    elif self.point_in_rect(pos, quit_btn):
                        pygame.quit()
                        sys.exit()

            self.clock.tick(30)

    def leaderboard_screen(self):
        back_btn = pygame.Rect(WIDTH // 2 - 70, HEIGHT - 60, 140, 40)

        while self.state == "leaderboard":
            rows = get_top_10()

            self.screen.fill((30, 50, 25))
            self.draw_text("Leaderboard", WIDTH // 2, 40, YELLOW, center=True, font=self.big_font)

            self.draw_text("Rank", 40, 90)
            self.draw_text("Username", 95, 90)
            self.draw_text("Score", 240, 90)
            self.draw_text("Level", 320, 90)
            self.draw_text("Date", 400, 90)

            y = 125
            for i, row in enumerate(rows, start=1):
                username, score, level, played_at = row
                date_str = played_at.strftime("%Y-%m-%d")
                self.draw_text(str(i), 40, y)
                self.draw_text(str(username), 95, y)
                self.draw_text(str(score), 240, y)
                self.draw_text(str(level), 320, y)
                self.draw_text(date_str, 400, y)
                y += 32

            self.draw_button(back_btn, "Back")
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.point_in_rect(event.pos, back_btn):
                        self.state = "menu"

            self.clock.tick(30)

    def settings_screen(self):
        back_btn = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 65, 180, 42)
        grid_btn = pygame.Rect(200, 140, 200, 45)
        sound_btn = pygame.Rect(200, 210, 200, 45)

        while self.state == "settings":
            self.screen.fill((30, 50, 25))
            self.draw_text("Settings", WIDTH // 2, 50, CYAN, center=True, font=self.big_font)

            self.draw_button(grid_btn, f"Grid: {'ON' if self.settings['grid'] else 'OFF'}")
            self.draw_button(sound_btn, f"Sound: {'ON' if self.settings['sound'] else 'OFF'}")
            self.draw_button(back_btn, "Save & Back")

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos

                    if self.point_in_rect(pos, grid_btn):
                        self.settings["grid"] = not self.settings["grid"]
                    elif self.point_in_rect(pos, sound_btn):
                        self.settings["sound"] = not self.settings["sound"]
                    elif self.point_in_rect(pos, back_btn):
                        self.save_settings()
                        self.state = "menu"

            self.clock.tick(30)

    def game_over_screen(self):
        retry_btn = pygame.Rect(WIDTH // 2 - 100, 260, 200, 45)
        menu_btn = pygame.Rect(WIDTH // 2 - 100, 320, 200, 45)

        self.save_game_result_once()
        current_best = get_personal_best(self.username.strip()) if self.username.strip() else 0

        while self.state == "game_over":
            self.screen.fill((30, 50, 25))
            self.draw_text("Game Over", WIDTH // 2, 90, RED, center=True, font=self.big_font)
            self.draw_text(f"Player: {self.username}", WIDTH // 2, 145, WHITE, center=True)
            self.draw_text(f"Score: {self.final_score}", WIDTH // 2, 180, WHITE, center=True)
            self.draw_text(f"Level reached: {self.final_level}", WIDTH // 2, 210, WHITE, center=True)
            self.draw_text(f"Best: {current_best}", WIDTH // 2, 240, YELLOW, center=True)

            self.draw_button(retry_btn, "Retry")
            self.draw_button(menu_btn, "Main Menu")

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.point_in_rect(event.pos, retry_btn):
                        self.personal_best = get_personal_best(self.username.strip())
                        self.reset_game()
                        self.state = "game"
                    elif self.point_in_rect(event.pos, menu_btn):
                        self.state = "menu"

            self.clock.tick(30)

    # ---------------- GAME DRAW ----------------
    def draw_food(self):
        x, y = self.food["pos"]
        px, py = x * CELL, y * CELL

        if self.sprites.get("apple"):
            self.screen.blit(self.sprites["apple"], (px, py))
        else:
            pygame.draw.circle(self.screen, self.food["color"], (px + CELL // 2, py + CELL // 2), CELL // 2 - 2)

    def draw_poison_food(self):
        x, y = self.poison_food["pos"]
        px, py = x * CELL, y * CELL

        pygame.draw.circle(self.screen, (120, 0, 0), (px + CELL // 2, py + CELL // 2), CELL // 2 - 2)
        pygame.draw.circle(self.screen, (180, 20, 20), (px + CELL // 2, py + CELL // 2), CELL // 2 - 6)

    def draw_powerup(self):
        if self.powerup is None:
            return

        x, y = self.powerup["pos"]
        px, py = x * CELL, y * CELL

        pygame.draw.rect(self.screen, self.powerup["color"], (px + 3, py + 3, CELL - 6, CELL - 6), border_radius=6)

        letter = "?"
        if self.powerup["type"] == "speed":
            letter = "S"
        elif self.powerup["type"] == "slow":
            letter = "M"
        elif self.powerup["type"] == "shield":
            letter = "H"

        text = self.small_font.render(letter, True, WHITE)
        rect = text.get_rect(center=(px + CELL // 2, py + CELL // 2))
        self.screen.blit(text, rect)

    def draw_obstacles(self):
        for block in self.obstacles:
            px, py = block[0] * CELL, block[1] * CELL
            pygame.draw.rect(self.screen, (100, 100, 100), (px, py, CELL, CELL), border_radius=4)
            pygame.draw.rect(self.screen, (70, 70, 70), (px + 2, py + 2, CELL - 4, CELL - 4), border_radius=4)

    # ---------------- GAME LOGIC ----------------
    def trigger_game_over(self):
        self.final_score = self.score
        self.final_level = self.level
        self.play_sound("gameover")
        self.state = "game_over"

    def handle_collision_with_protection(self, new_head):
        wrapped_head = (new_head[0] % COLS, new_head[1] % ROWS)

        hit_self = wrapped_head in self.snake
        hit_obstacle = wrapped_head in self.obstacles

        if hit_self:
            if self.shield:
                self.shield = False
                self.active_effect = None
                return wrapped_head
            return None

        if hit_obstacle:
            return None

        return wrapped_head

    def game_loop(self):
        while self.state == "game":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.dy == 0:
                        self.dx, self.dy = 0, -1
                    elif event.key == pygame.K_DOWN and self.dy == 0:
                        self.dx, self.dy = 0, 1
                    elif event.key == pygame.K_LEFT and self.dx == 0:
                        self.dx, self.dy = -1, 0
                    elif event.key == pygame.K_RIGHT and self.dx == 0:
                        self.dx, self.dy = 1, 0

            now = pygame.time.get_ticks()

            should_move = False
            if now - self.last_move_time >= self.move_delay:
                self.prev_snake = self.snake[:]
                self.last_move_time += self.move_delay
                should_move = True

            if now - self.food["spawn_time"] > self.food["time"]:
                self.food = self.generate_food()

            if now - self.poison_food["spawn_time"] > self.poison_food["time"]:
                self.poison_food = self.generate_poison_food()

            if self.powerup is None and now - self.last_powerup_spawn > 6000:
                self.powerup = self.generate_powerup()
                self.last_powerup_spawn = now

            if self.powerup is not None and now - self.powerup["spawn_time"] > self.powerup["field_time"]:
                self.powerup = None

            self.update_effects()

            if should_move:
                head_x, head_y = self.snake[0]
                raw_new_head = (head_x + self.dx, head_y + self.dy)
                checked_head = self.handle_collision_with_protection(raw_new_head)

                if checked_head is None:
                    self.trigger_game_over()
                    return

                new_head = checked_head
                self.snake.insert(0, new_head)

                grew = False
                ate_poison = False

                if new_head == self.food["pos"]:
                    self.score += self.food["score"]
                    self.food_eaten += 1
                    grew = True
                    self.play_sound("eat")
                    self.food = self.generate_food()

                    if self.food_eaten % 4 == 0:
                        self.level_up()

                elif new_head == self.poison_food["pos"]:
                    self.score = max(0, self.score - 1)
                    ate_poison = True
                    self.play_sound("poison")
                    self.show_message("-1 score", 800)
                    self.poison_food = self.generate_poison_food()

                    if len(self.snake) > 1:
                        self.snake.pop()

                elif self.powerup is not None and new_head == self.powerup["pos"]:
                    self.activate_powerup(self.powerup["type"])
                    self.play_sound("powerup")
                    self.powerup = None

                if not grew and not ate_poison:
                    self.snake.pop()

            alpha = (now - self.last_move_time) / self.move_delay if self.move_delay > 0 else 1
            alpha = max(0, min(1, alpha))

            self.draw_checker_background()

            if self.settings["grid"]:
                self.draw_grid()

            self.draw_obstacles()
            self.draw_food()
            self.draw_poison_food()
            self.draw_powerup()
            self.draw_snake(alpha)

            self.draw_text(f"Score: {self.score}", 10, 10, WHITE)

            if self.shield:
                self.draw_text("Shield", WIDTH - 100, 10, PURPLE)
            elif self.active_effect == "speed":
                self.draw_text("Speed", WIDTH - 100, 10, ORANGE)
            elif self.active_effect == "slow":
                self.draw_text("Slow", WIDTH - 100, 10, CYAN)

            self.draw_top_message()

            pygame.display.flip()
            self.clock.tick(FPS)

    # ---------------- RUN ----------------
    def run(self):
        while True:
            if self.state == "menu":
                self.menu_screen()
            elif self.state == "game":
                self.game_loop()
            elif self.state == "leaderboard":
                self.leaderboard_screen()
            elif self.state == "settings":
                self.settings_screen()
            elif self.state == "game_over":
                self.game_over_screen()