import pygame
import math

pygame.init()

WIDTH, HEIGHT = 1100, 700
TOOLBAR_HEIGHT = 80
CANVAS_Y = TOOLBAR_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint App")
clock = pygame.time.Clock()

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)

font = pygame.font.SysFont(None, 28)

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# states
current_tool = "brush"
current_color = BLACK
brush_size = 5
drawing = False
start_pos = None
last_pos = None

# button class
class Button:
    def __init__(self, x, y, w, h, text="", color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, surface, active=False, is_color_button=False):
        fill_color = self.color if is_color_button else (LIGHT_BLUE if active else self.color)

        pygame.draw.rect(surface, fill_color, self.rect)

        border_width = 4 if active else 2
        pygame.draw.rect(surface, BLACK, self.rect, border_width)

        if self.text:
            text_surf = font.render(self.text, True, BLACK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


tool_buttons = [
    Button(10, 20, 100, 40, "Brush"),
    Button(120, 20, 120, 40, "Rectangle"),
    Button(250, 20, 100, 40, "Circle"),
    Button(360, 20, 100, 40, "Eraser"),
    Button(470, 20, 100, 40, "Clear"),
    Button(580, 20, 40, 40, "-"),
    Button(630, 20, 40, 40, "+"),
]

color_buttons = [
    Button(720, 20, 40, 40, color=RED),
    Button(770, 20, 40, 40, color=GREEN),
    Button(820, 20, 40, 40, color=BLUE),
    Button(870, 20, 40, 40, color=YELLOW),
    Button(920, 20, 40, 40, color=PURPLE),
    Button(970, 20, 40, 40, color=BLACK),
]

color_values = [RED, GREEN, BLUE, YELLOW, PURPLE, BLACK]


def draw_toolbar():
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    for button in tool_buttons:
        active = (
            (button.text == "Brush" and current_tool == "brush") or
            (button.text == "Rectangle" and current_tool == "rect") or
            (button.text == "Circle" and current_tool == "circle") or
            (button.text == "Eraser" and current_tool == "eraser")
        )
        button.draw(screen, active=active)

    for i, button in enumerate(color_buttons):
        active = (current_color == color_values[i])
        button.draw(screen, active=active, is_color_button=True)

    size_text = font.render(f"Size: {brush_size}", True, WHITE)
    screen.blit(size_text, (580, 62))


def draw_line(surface, color, start, end, radius):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = max(abs(dx), abs(dy))

    if distance == 0:
        pygame.draw.circle(surface, color, start, radius)
        return

    for i in range(distance + 1):
        t = i / distance
        x = int(start[0] + dx * t)
        y = int(start[1] + dy * t)
        pygame.draw.circle(surface, color, (x, y), radius)


def make_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    return pygame.Rect(left, top, width, height)


def draw_circle_from_drag(surface, color, start, end, width=2):
    center_x = (start[0] + end[0]) // 2
    center_y = (start[1] + end[1]) // 2
    radius = int(math.hypot(end[0] - start[0], end[1] - start[1]) / 2)

    if radius > 0:
        pygame.draw.circle(surface, color, (center_x, center_y), radius, width)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if event.button == 1:
                if my <= TOOLBAR_HEIGHT:
                    for button in tool_buttons:
                        if button.is_clicked(event.pos):
                            if button.text == "Brush":
                                current_tool = "brush"
                            elif button.text == "Rectangle":
                                current_tool = "rect"
                            elif button.text == "Circle":
                                current_tool = "circle"
                            elif button.text == "Eraser":
                                current_tool = "eraser"
                            elif button.text == "Clear":
                                canvas.fill(WHITE)
                            elif button.text == "+":
                                brush_size = min(50, brush_size + 1)
                            elif button.text == "-":
                                brush_size = max(1, brush_size - 1)

                    for i, button in enumerate(color_buttons):
                        if button.is_clicked(event.pos):
                            current_color = color_values[i]

                else:
                    drawing = True
                    start_pos = (mx, my - TOOLBAR_HEIGHT)
                    last_pos = (mx, my - TOOLBAR_HEIGHT)

                    if current_tool == "brush":
                        pygame.draw.circle(canvas, current_color, start_pos, brush_size)
                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, start_pos, brush_size)

            elif event.button == 4:  
                brush_size = min(50, brush_size + 1)
            elif event.button == 5:
                brush_size = max(1, brush_size - 1)

        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                mx, my = event.pos
                if my > TOOLBAR_HEIGHT:
                    current_pos = (mx, my - TOOLBAR_HEIGHT)

                    if current_tool == "brush":
                        draw_line(canvas, current_color, last_pos, current_pos, brush_size)
                        last_pos = current_pos
                    elif current_tool == "eraser":
                        draw_line(canvas, WHITE, last_pos, current_pos, brush_size)
                        last_pos = current_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                mx, my = event.pos
                if my > TOOLBAR_HEIGHT:
                    end_pos = (mx, my - TOOLBAR_HEIGHT)

                    if current_tool == "rect":
                        rect = make_rect(start_pos, end_pos)
                        pygame.draw.rect(canvas, current_color, rect, 2)

                    elif current_tool == "circle":
                        draw_circle_from_drag(canvas, current_color, start_pos, end_pos, 2)

                drawing = False
                start_pos = None
                last_pos = None

    screen.fill(WHITE)
    draw_toolbar()
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    # preview shape while dragging
    if drawing and current_tool in ("rect", "circle"):
        mx, my = pygame.mouse.get_pos()
        if my > TOOLBAR_HEIGHT:
            preview = canvas.copy()
            current_pos = (mx, my - TOOLBAR_HEIGHT)

            if current_tool == "rect":
                rect = make_rect(start_pos, current_pos)
                pygame.draw.rect(preview, current_color, rect, 2)
            elif current_tool == "circle":
                draw_circle_from_drag(preview, current_color, start_pos, current_pos, 2)

            screen.blit(preview, (0, TOOLBAR_HEIGHT))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()