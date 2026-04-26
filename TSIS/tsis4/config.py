# config.py

CELL = 20
COLS = 30
ROWS = 26

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

FPS = 120
BASE_SNAKE_SPEED = 8

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (120, 120, 120)

GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
DARK_RED = (120, 0, 0)
YELLOW = (255, 215, 0)
BLUE = (50, 150, 255)
PURPLE = (180, 80, 255)
CYAN = (0, 220, 220)
ORANGE = (255, 140, 0)

TITLE = "Snake"

FOOD_TYPES = [
    {"score": 1, "color": RED, "time": 7000},
    {"score": 2, "color": YELLOW, "time": 5000},
    {"score": 3, "color": BLUE, "time": 3000},
]

POWERUP_TYPES = {
    "speed": {
        "color": ORANGE,
        "duration": 5000,
        "field_time": 8000
    },
    "slow": {
        "color": CYAN,
        "duration": 5000,
        "field_time": 8000
    },
    "shield": {
        "color": PURPLE,
        "duration": None,
        "field_time": 8000
    }
}

DEFAULT_SETTINGS = {
    "snake_color": [0, 200, 0],
    "grid": True,
    "sound": True
}