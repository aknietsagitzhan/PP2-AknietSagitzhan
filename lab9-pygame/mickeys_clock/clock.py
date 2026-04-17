from __future__ import annotations

import sys
import time
from pathlib import Path

import pygame


class MickeyClock:
    def __init__(self) -> None:
        pygame.init()

        self.base_dir = Path(__file__).resolve().parent
        self.images_dir = self.base_dir / "images"

        self.width = 800
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Mickey's Clock")

        self.fps_clock = pygame.time.Clock()

        self.clock_face = self.load_image("clock_face.png")
        self.right_hand = self.load_image("right_hand.png")   
        self.left_hand = self.load_image("left_hand.png")     

        face_size = 800
        self.clock_face = pygame.transform.smoothscale(self.clock_face, (face_size, face_size))

        self.right_hand = pygame.transform.smoothscale(self.right_hand, (600, 900))
        self.left_hand = pygame.transform.smoothscale(self.left_hand, (600, 900))

        self.center = (self.width // 2, self.height // 2)

        self.right_pivot = (self.right_hand.get_width() // 2, 450)
        self.left_pivot = (self.left_hand.get_width() // 2, 450)

        self.last_second = -1

    def load_image(self, filename: str) -> pygame.Surface:
        path = self.images_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing image: {path}")
        return pygame.image.load(str(path)).convert_alpha()

    def get_angles(self) -> tuple[float, float]:
        now = time.localtime()
        minute = now.tm_min
        second = now.tm_sec

        minute_angle = minute * 6 + second * 0.1
        second_angle = second * 6

        return minute_angle, second_angle

    def draw_rotated(
        self,
        surface: pygame.Surface,
        image: pygame.Surface,
        pivot_world: tuple[int, int],
        pivot_image: tuple[int, int],
        angle_clockwise: float,
    ) -> None:
        image_rect = image.get_rect(
            topleft=(pivot_world[0] - pivot_image[0], pivot_world[1] - pivot_image[1])
        )

        offset = pygame.math.Vector2(pivot_world) - image_rect.center
        rotated_offset = offset.rotate(angle_clockwise)

        rotated_center = (
            pivot_world[0] - rotated_offset.x,
            pivot_world[1] - rotated_offset.y,
        )

        rotated_image = pygame.transform.rotozoom(image, -angle_clockwise, 1.0)
        rotated_rect = rotated_image.get_rect(center=rotated_center)
        surface.blit(rotated_image, rotated_rect)

    def draw(self) -> None:
        self.screen.fill((235, 235, 235))

        face_rect = self.clock_face.get_rect(center=self.center)
        self.screen.blit(self.clock_face, face_rect)

        minute_angle, second_angle = self.get_angles()

        self.draw_rotated(
            self.screen,
            self.right_hand,
            self.center,
            self.right_pivot,
            minute_angle + 180,
        )

        self.draw_rotated(
            self.screen,
            self.left_hand,
            self.center,
            self.left_pivot,
            second_angle + 180,
        )

        pygame.display.flip()

    def run(self) -> None:
        self.draw()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            current_second = time.localtime().tm_sec
            if current_second != self.last_second:
                self.last_second = current_second
                self.draw()

            self.fps_clock.tick(30)