import pygame
import math
from datetime import datetime
from collections import deque

pygame.init()

# -----------------------------
# Screen settings
# -----------------------------
WIDTH, HEIGHT = 1100, 700
TOOLBAR_HEIGHT = 160
CANVAS_Y = TOOLBAR_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint App Extended")
clock = pygame.time.Clock()

# -----------------------------
# Colors
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (205, 205, 205)
DARK_GRAY = (60, 60, 60)
LIGHT_BLUE = (170, 215, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 230, 0)
PURPLE = (180, 0, 255)
ORANGE = (255, 140, 0)
PINK = (255, 105, 180)
BROWN = (139, 69, 19)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIME = (150, 255, 0)
NAVY = (0, 0, 128)
MAROON = (128, 0, 0)

font = pygame.font.SysFont(None, 22)
small_font = pygame.font.SysFont(None, 19)
text_font = pygame.font.SysFont(None, 34)

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# -----------------------------
# Program state
# -----------------------------
current_tool = "pencil"
current_color = BLACK
brush_size = 5

BRUSH_SIZES = {
    "small": 2,
    "medium": 5,
    "large": 10,
}

MIN_BRUSH_SIZE = 1
MAX_BRUSH_SIZE = 50

drawing = False
start_pos = None
last_pos = None

# Text tool state
text_active = False
text_pos = None
text_value = ""

# -----------------------------
# Button class
# -----------------------------
class Button:
    def __init__(self, x, y, w, h, text="", color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, surface, active=False, is_color_button=False):
        fill_color = self.color if is_color_button else (LIGHT_BLUE if active else self.color)
        pygame.draw.rect(surface, fill_color, self.rect, border_radius=7)
        pygame.draw.rect(surface, BLACK, self.rect, 4 if active else 2, border_radius=7)

        if self.text:
            text_surface = font.render(self.text, True, BLACK)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# -----------------------------
# Clean toolbar layout
# -----------------------------
tool_buttons = []

# Row 1: main tools
x = 10
y = 10
for text, width in [
    ("Pencil", 70),
    ("Line", 60),
    ("Eraser", 70),
    ("Rect", 60),
    ("Circle", 70),
    ("Square", 75),
    ("RightTri", 85),
    ("EquiTri", 85),
    ("Rhombus", 85),
    ("Fill", 60),
    ("Text", 60),
    ("Clear", 65),
]:
    tool_buttons.append(Button(x, y, width, 30, text))
    x += width + 8

# Row 2: size buttons only
size_buttons = [
    Button(10, 65, 65, 28, "Small"),
    Button(83, 65, 75, 28, "Medium"),
    Button(166, 65, 65, 28, "Large"),
    Button(250, 65, 34, 28, "-"),
    Button(292, 65, 34, 28, "+"),
]

# Extra colors, no white color button. Eraser still uses white.
color_values = [
    BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE,
    PINK, BROWN, CYAN, MAGENTA, LIME, NAVY, MAROON
]

# Row 3: colors are on their own row, so nothing overlaps
color_buttons = []
color_start_x = 10
color_start_y = 112
color_size = 26
color_gap = 8

for i, color in enumerate(color_values):
    x = color_start_x + i * (color_size + color_gap)
    color_buttons.append(Button(x, color_start_y, color_size, color_size, color=color))

# -----------------------------
# Coordinate helpers
# -----------------------------
def canvas_pos(screen_pos):
    x, y = screen_pos
    return x, y - TOOLBAR_HEIGHT


def inside_canvas(screen_pos):
    x, y = screen_pos
    return 0 <= x < WIDTH and TOOLBAR_HEIGHT <= y < HEIGHT

# -----------------------------
# Drawing helpers
# -----------------------------
def draw_smooth_line(surface, color, start, end, width):
    pygame.draw.line(surface, color, start, end, width)
    radius = max(1, width // 2)
    pygame.draw.circle(surface, color, start, radius)
    pygame.draw.circle(surface, color, end, radius)


def normalize_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def draw_rectangle(surface, color, start, end, width):
    pygame.draw.rect(surface, color, normalize_rect(start, end), width)


def draw_circle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    radius = int(math.hypot(x2 - x1, y2 - y1))
    if radius > 0:
        pygame.draw.circle(surface, color, start, radius, width)


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
    if side == 0:
        return
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
    width = brush_size
    if tool == "line":
        draw_smooth_line(surface, color, start, end, width)
    elif tool == "rect":
        draw_rectangle(surface, color, start, end, width)
    elif tool == "circle":
        draw_circle(surface, color, start, end, width)
    elif tool == "square":
        draw_square(surface, color, start, end, width)
    elif tool == "right_triangle":
        draw_right_triangle(surface, color, start, end, width)
    elif tool == "equi_triangle":
        draw_equilateral_triangle(surface, color, start, end, width)
    elif tool == "rhombus":
        draw_rhombus(surface, color, start, end, width)


def flood_fill(surface, pos, new_color):
    width, height = surface.get_size()
    x, y = pos

    if not (0 <= x < width and 0 <= y < height):
        return

    target_color = surface.get_at((x, y))
    replacement_color = pygame.Color(*new_color)

    if target_color == replacement_color:
        return

    queue = deque([(x, y)])

    while queue:
        px, py = queue.popleft()

        if px < 0 or px >= width or py < 0 or py >= height:
            continue
        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), replacement_color)

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def save_canvas():
    filename = datetime.now().strftime("paint_%Y%m%d_%H%M%S.png")
    pygame.image.save(canvas, filename)
    print(f"Saved: {filename}")


def tool_from_button(text):
    return {
        "Pencil": "pencil",
        "Line": "line",
        "Eraser": "eraser",
        "Rect": "rect",
        "Circle": "circle",
        "Square": "square",
        "RightTri": "right_triangle",
        "EquiTri": "equi_triangle",
        "Rhombus": "rhombus",
        "Fill": "fill",
        "Text": "text",
    }.get(text)


def button_active(button):
    mapping = tool_from_button(button.text)
    return mapping == current_tool


def change_brush_size(amount):
    global brush_size
    brush_size = max(MIN_BRUSH_SIZE, min(MAX_BRUSH_SIZE, brush_size + amount))


def draw_toolbar():
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    # Labels
    screen.blit(small_font.render("SIZE", True, WHITE), (16, 50))
    screen.blit(small_font.render("COLORS", True, WHITE), (10, 96))

    for button in tool_buttons:
        button.draw(screen, active=button_active(button))

    for button in size_buttons:
        active = (
            (button.text == "Small" and brush_size == BRUSH_SIZES["small"]) or
            (button.text == "Medium" and brush_size == BRUSH_SIZES["medium"]) or
            (button.text == "Large" and brush_size == BRUSH_SIZES["large"])
        )
        button.draw(screen, active=active)

    for i, button in enumerate(color_buttons):
        button.draw(screen, active=current_color == color_values[i], is_color_button=True)

    # Current color + help text on the right side, away from buttons
    current_color_box = pygame.Rect(360, 65, 32, 28)
    pygame.draw.rect(screen, current_color, current_color_box, border_radius=6)
    pygame.draw.rect(screen, BLACK, current_color_box, 2, border_radius=6)

    info1 = font.render(f"Tool: {current_tool} | Brush: {brush_size}px", True, WHITE)
    info2 = small_font.render("Keys: 1/2/3 presets | +/- resize | Ctrl+S save", True, WHITE)
    screen.blit(info1, (405, 64))
    screen.blit(info2, (405, 88))

# -----------------------------
# Main loop
# -----------------------------
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                if event.key == pygame.K_s:
                    save_canvas()

            elif text_active:
                if event.key == pygame.K_RETURN:
                    rendered = text_font.render(text_value, True, current_color)
                    canvas.blit(rendered, text_pos)
                    text_active = False
                    text_value = ""
                    text_pos = None
                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_value = ""
                    text_pos = None
                elif event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]
                else:
                    text_value += event.unicode

            else:
                if event.key == pygame.K_1:
                    brush_size = BRUSH_SIZES["small"]
                elif event.key == pygame.K_2:
                    brush_size = BRUSH_SIZES["medium"]
                elif event.key == pygame.K_3:
                    brush_size = BRUSH_SIZES["large"]
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    change_brush_size(1)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    change_brush_size(-1)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Mouse wheel also changes brush size
            if event.button == 4:
                change_brush_size(1)
                continue
            elif event.button == 5:
                change_brush_size(-1)
                continue

            if event.button != 1:
                continue

            mx, my = event.pos

            if my <= TOOLBAR_HEIGHT:
                for button in tool_buttons:
                    if button.is_clicked(event.pos):
                        if button.text == "Clear":
                            canvas.fill(WHITE)
                        else:
                            selected = tool_from_button(button.text)
                            if selected:
                                current_tool = selected
                                text_active = False

                for button in size_buttons:
                    if button.is_clicked(event.pos):
                        if button.text == "Small":
                            brush_size = BRUSH_SIZES["small"]
                        elif button.text == "Medium":
                            brush_size = BRUSH_SIZES["medium"]
                        elif button.text == "Large":
                            brush_size = BRUSH_SIZES["large"]
                        elif button.text == "+":
                            change_brush_size(1)
                        elif button.text == "-":
                            change_brush_size(-1)

                for i, button in enumerate(color_buttons):
                    if button.is_clicked(event.pos):
                        current_color = color_values[i]

            elif inside_canvas(event.pos):
                pos = canvas_pos(event.pos)

                if current_tool == "fill":
                    flood_fill(canvas, pos, current_color)

                elif current_tool == "text":
                    text_active = True
                    text_pos = pos
                    text_value = ""

                else:
                    drawing = True
                    start_pos = pos
                    last_pos = pos

                    if current_tool == "pencil":
                        pygame.draw.circle(canvas, current_color, pos, max(1, brush_size // 2))
                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, pos, max(1, brush_size // 2))

        elif event.type == pygame.MOUSEMOTION:
            if drawing and inside_canvas(event.pos):
                current_pos = canvas_pos(event.pos)

                if current_tool == "pencil":
                    draw_smooth_line(canvas, current_color, last_pos, current_pos, brush_size)
                    last_pos = current_pos

                elif current_tool == "eraser":
                    draw_smooth_line(canvas, WHITE, last_pos, current_pos, brush_size)
                    last_pos = current_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                if inside_canvas(event.pos):
                    end_pos = canvas_pos(event.pos)

                    if current_tool not in ("pencil", "eraser"):
                        draw_selected_shape(canvas, current_tool, current_color, start_pos, end_pos)

                drawing = False
                start_pos = None
                last_pos = None

    screen.fill(WHITE)
    draw_toolbar()
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    # Live preview for line and shapes
    if drawing and current_tool not in ("pencil", "eraser"):
        mx, my = pygame.mouse.get_pos()
        if my > TOOLBAR_HEIGHT:
            preview = canvas.copy()
            current_pos = (mx, my - TOOLBAR_HEIGHT)
            draw_selected_shape(preview, current_tool, current_color, start_pos, current_pos)
            screen.blit(preview, (0, TOOLBAR_HEIGHT))

    # Live text preview
    if text_active and text_pos is not None:
        preview_text = text_font.render(text_value + "|", True, current_color)
        screen.blit(preview_text, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
