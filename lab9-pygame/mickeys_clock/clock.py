from datetime import datetime
import pygame


class MickeyClock:
    def __init__(self, center, clock_image_path, screen_size):
        self.center = center
        self.screen_width, self.screen_height = screen_size

        # Fill the whole window
        self.clock_img = pygame.image.load(clock_image_path).convert_alpha()
        self.clock_img = pygame.transform.smoothscale(
            self.clock_img,
            (self.screen_width, self.screen_height)
        )

        # Scale hand sizes based on window size
        base_size = min(self.screen_width, self.screen_height)
        self.minute_hand = self.create_hand_surface(
            length=int(base_size * 0.23),
            hand_side="right",
            thickness=max(6, int(base_size * 0.014))
        )
        self.second_hand = self.create_hand_surface(
            length=int(base_size * 0.30),
            hand_side="left",
            thickness=max(6, int(base_size * 0.014))
        )

        self.center_dot_radius = max(4, int(base_size * 0.008))

    def create_hand_surface(self, length, hand_side, thickness):
        width = max(90, int(length * 0.75))
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
            thickness
        )

        # glove palm
        palm_radius = max(12, int(length * 0.13))
        palm_center = (pivot_x, 42)
        pygame.draw.circle(surface, glove_color, palm_center, palm_radius)
        pygame.draw.circle(surface, outline, palm_center, palm_radius, 2)

        # thumb
        thumb_offset = max(12, int(length * 0.13))
        thumb_radius = max(7, int(length * 0.07))
        if hand_side == "left":
            thumb_center = (pivot_x - thumb_offset, 46)
        else:
            thumb_center = (pivot_x + thumb_offset, 46)

        pygame.draw.circle(surface, glove_color, thumb_center, thumb_radius)
        pygame.draw.circle(surface, outline, thumb_center, thumb_radius, 2)

        # fingers
        finger_offsets = [-18, -6, 6, 18]
        finger_w = max(10, int(length * 0.08))
        finger_h = max(20, int(length * 0.16))

        for dx in finger_offsets:
            finger_center = (pivot_x + dx, 20)
            rect = (
                finger_center[0] - finger_w // 2,
                finger_center[1] - finger_h // 2,
                finger_w,
                finger_h
            )
            pygame.draw.ellipse(surface, glove_color, rect)
            pygame.draw.ellipse(surface, outline, rect, 2)

        return surface

    def get_angles(self):
        now = datetime.now()
        minute = now.minute
        second = now.second

        minute_angle = (minute + second / 60) * 6
        second_angle = second * 6

        return minute_angle, second_angle

    def blit_rotated_hand(self, screen, image, angle_degrees):
        image_rect = image.get_rect()
        pivot = pygame.math.Vector2(image_rect.width / 2, image_rect.height - 20)
        original_center = pygame.math.Vector2(image_rect.center)
        offset = original_center - pivot

        rotated_image = pygame.transform.rotate(image, -angle_degrees)
        rotated_offset = offset.rotate(angle_degrees)

        draw_center = (
            self.center[0] + rotated_offset.x,
            self.center[1] + rotated_offset.y
        )

        rotated_rect = rotated_image.get_rect(center=draw_center)
        screen.blit(rotated_image, rotated_rect)

    def draw(self, screen):
        # background clock fills the whole window
        screen.blit(self.clock_img, (0, 0))

        minute_angle, second_angle = self.get_angles()

        # right hand = minutes
        self.blit_rotated_hand(screen, self.minute_hand, minute_angle)

        # left hand = seconds
        self.blit_rotated_hand(screen, self.second_hand, second_angle)

        pygame.draw.circle(screen, (0, 0, 0), self.center, self.center_dot_radius)