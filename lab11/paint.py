import pygame
import math


pygame.init()

# -----------------------------
# Screen settings
# -----------------------------
WIDTH, HEIGHT = 1100, 700
TOOLBAR_HEIGHT = 90
CANVAS_Y = TOOLBAR_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint App Extended")
clock = pygame.time.Clock()

# -----------------------------
# Colors
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 230, 0)
PURPLE = (180, 0, 255)
ORANGE = (255, 140, 0)

font = pygame.font.SysFont(None, 24)

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# -----------------------------
# Program state
# -----------------------------
current_tool = "brush"
current_color = BLACK
brush_size = 5
# Fill mode removed (only outline drawing is used)

drawing = False
start_pos = None
last_pos = None


# -----------------------------
# Button class
# -----------------------------
class Button:
    def __init__(self, x, y, w, h, text="", color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, surface, active=False, is_color_button=False):
        if is_color_button:
            fill_color = self.color
        else:
            fill_color = LIGHT_BLUE if active else self.color

        pygame.draw.rect(surface, fill_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, BLACK, self.rect, 4 if active else 2, border_radius=6)

        if self.text:
            text_surface = font.render(self.text, True, BLACK)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# -----------------------------
# Tool buttons (added ERASER)
# -----------------------------
tool_buttons = [
    Button(10, 15, 80, 35, "Brush"),
    Button(100, 15, 85, 35, "Eraser"),
    Button(195, 15, 85, 35, "Square"),
    Button(290, 15, 105, 35, "RightTri"),
    Button(405, 15, 105, 35, "EquiTri"),
    Button(520, 15, 100, 35, "Rhombus"),
        Button(710, 15, 70, 35, "Clear"),
    Button(790, 15, 40, 35, "-"),
    Button(840, 15, 40, 35, "+"),
]

# -----------------------------
# Color buttons
# -----------------------------
color_buttons = [
    Button(900, 15, 35, 35, color=BLACK),
    Button(940, 15, 35, 35, color=RED),
    Button(980, 15, 35, 35, color=GREEN),
    Button(1020, 15, 35, 35, color=BLUE),
]

color_values = [BLACK, RED, GREEN, BLUE]


# -----------------------------
# Drawing helpers
# -----------------------------
def get_draw_width():
    """Always return outline width (fill removed)."""
    return 2


def draw_smooth_line(surface, color, start, end, radius):
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


def draw_square(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    size = min(abs(x2 - x1), abs(y2 - y1))
    left = x1 if x2 >= x1 else x1 - size
    top = y1 if y2 >= y1 else y1 - size
    pygame.draw.rect(surface, color, (left, top, size, size), width)


def draw_right_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    pygame.draw.polygon(surface, color, [(x1, y1), (x2, y1), (x1, y2)], width)


def draw_equilateral_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    side = abs(x2 - x1)
    height = int(side * math.sqrt(3) / 2)
    direction = -1 if y2 < y1 else 1
    p1 = (x1, y1)
    p2 = (x1 + side if x2 >= x1 else x1 - side, y1)
    p3 = ((p1[0] + p2[0]) // 2, y1 + direction * height)
    pygame.draw.polygon(surface, color, [p1, p2, p3], width)


def draw_rhombus(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    pygame.draw.polygon(surface, color, [(cx, y1), (x2, cy), (cx, y2), (x1, cy)], width)


def draw_selected_shape(surface, tool, color, start, end):
    width = get_draw_width()
    if tool == "square":
        draw_square(surface, color, start, end, width)
    elif tool == "right_triangle":
        draw_right_triangle(surface, color, start, end, width)
    elif tool == "equi_triangle":
        draw_equilateral_triangle(surface, color, start, end, width)
    elif tool == "rhombus":
        draw_rhombus(surface, color, start, end, width)


def draw_toolbar():
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    for button in tool_buttons:
        active = (
            (button.text == "Brush" and current_tool == "brush") or
            (button.text == "Eraser" and current_tool == "eraser") or
            (button.text == "Square" and current_tool == "square") or
            (button.text == "RightTri" and current_tool == "right_triangle") or
            (button.text == "EquiTri" and current_tool == "equi_triangle") or
            (button.text == "Rhombus" and current_tool == "rhombus") or
            (button.text == "Fill" and fill_shapes)
        )
        button.draw(screen, active=active)

    for i, button in enumerate(color_buttons):
        active = current_color == color_values[i]
        button.draw(screen, active=active, is_color_button=True)

    mode = "Outline"
    info = font.render(f"Size: {brush_size} ", True, WHITE)
    screen.blit(info, (10, 60))


# -----------------------------
# Main loop
# -----------------------------
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
                            if button.text == "Brush": current_tool = "brush"
                            elif button.text == "Eraser": current_tool = "eraser"
                            elif button.text == "Square": current_tool = "square"
                            elif button.text == "RightTri": current_tool = "right_triangle"
                            elif button.text == "EquiTri": current_tool = "equi_triangle"
                            elif button.text == "Rhombus": current_tool = "rhombus"
                            
                            elif button.text == "Clear": canvas.fill(WHITE)
                            elif button.text == "+": brush_size = min(50, brush_size + 1)
                            elif button.text == "-": brush_size = max(1, brush_size - 1)

                    for i, button in enumerate(color_buttons):
                        if button.is_clicked(event.pos):
                            current_color = color_values[i]

                else:
                    drawing = True
                    start_pos = (mx, my - TOOLBAR_HEIGHT)
                    last_pos = start_pos

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
                        draw_smooth_line(canvas, current_color, last_pos, current_pos, brush_size)
                        last_pos = current_pos

                    elif current_tool == "eraser":
                        draw_smooth_line(canvas, WHITE, last_pos, current_pos, brush_size)
                        last_pos = current_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                mx, my = event.pos
                if my > TOOLBAR_HEIGHT:
                    end_pos = (mx, my - TOOLBAR_HEIGHT)

                    if current_tool not in ("brush", "eraser"):
                        draw_selected_shape(canvas, current_tool, current_color, start_pos, end_pos)

                drawing = False
                start_pos = None
                last_pos = None

    screen.fill(WHITE)
    draw_toolbar()
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    # Preview shapes
    if drawing and current_tool not in ("brush", "eraser"):
        mx, my = pygame.mouse.get_pos()
        if my > TOOLBAR_HEIGHT:
            preview = canvas.copy()
            current_pos = (mx, my - TOOLBAR_HEIGHT)
            draw_selected_shape(preview, current_tool, current_color, start_pos, current_pos)
            screen.blit(preview, (0, TOOLBAR_HEIGHT))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()