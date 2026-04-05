import math
from datetime import datetime

import pygame


class MickeyClock:
    def __init__(self, center, clock_image_path):
        self.center = center

        self.clock_img = pygame.image.load(clock_image_path).convert_alpha()
        self.clock_img = pygame.transform.scale(self.clock_img, (420, 420))

        self.minute_hand = self.create_hand_surface(length=120, hand_side="right")
        self.second_hand = self.create_hand_surface(length=150, hand_side="left")

    def create_hand_surface(self, length, hand_side):
        width = 120
        height = length + 40

        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pivot_x = width // 2
        pivot_y = height - 20

        arm_color = (30, 30, 30)
        glove_color = (255, 255, 255)
        outline = (0, 0, 0)

        # arm
        pygame.draw.line(
            surface,
            arm_color,
            (pivot_x, pivot_y),
            (pivot_x, 55),
            10
        )

        # glove palm
        palm_center = (pivot_x, 42)
        pygame.draw.circle(surface, glove_color, palm_center, 16)
        pygame.draw.circle(surface, outline, palm_center, 16, 2)

        # thumb
        thumb_center = (pivot_x - 16, 46) if hand_side == "left" else (pivot_x + 16, 46)
        pygame.draw.circle(surface, glove_color, thumb_center, 9)
        pygame.draw.circle(surface, outline, thumb_center, 9, 2)

        # fingers
        finger_offsets = [-18, -6, 6, 18]
        for dx in finger_offsets:
            finger_center = (pivot_x + dx, 20)
            pygame.draw.ellipse(
                surface,
                glove_color,
                (finger_center[0] - 6, finger_center[1] - 13, 12, 26)
            )
            pygame.draw.ellipse(
                surface,
                outline,
                (finger_center[0] - 6, finger_center[1] - 13, 12, 26),
                2
            )

        return surface

    def get_angles(self):
        now = datetime.now()
        minute = now.minute
        second = now.second

        minute_angle = minute * 6
        second_angle = second * 6

        return minute_angle, second_angle

    def blit_rotated_hand(self, screen, image, angle_degrees):
        image_rect = image.get_rect()
        original_center = pygame.math.Vector2(image_rect.center)

        pivot = pygame.math.Vector2(image_rect.width / 2, image_rect.height - 20)
        pivot_to_center = original_center - pivot

        rotated_image = pygame.transform.rotate(image, -angle_degrees)
        rotated_offset = pivot_to_center.rotate(angle_degrees)

        draw_center = (
            self.center[0] + rotated_offset.x,
            self.center[1] + rotated_offset.y
        )

        rotated_rect = rotated_image.get_rect(center=draw_center)
        screen.blit(rotated_image, rotated_rect)

    def draw(self, screen):
        clock_rect = self.clock_img.get_rect(center=self.center)
        screen.blit(self.clock_img, clock_rect)

        minute_angle, second_angle = self.get_angles()

        # right hand = minutes
        self.blit_rotated_hand(screen, self.minute_hand, minute_angle)

        # left hand = seconds
        self.blit_rotated_hand(screen, self.second_hand, second_angle)

        pygame.draw.circle(screen, (0, 0, 0), self.center, 5)