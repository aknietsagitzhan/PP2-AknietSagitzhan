import pygame
import random
import sys
import os

pygame.init() #zapusk pygame
pygame.mixer.init() #zapusk zvuka

# -----------------------------
# WINDOW
# -----------------------------
WIDTH = 400
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()
FPS = 60

# -----------------------------
# SPEED SETTINGS
# -----------------------------
MAX_SPEED_KMH = 200
AUTO_ACCELERATION = 18      # km/h per second
GAS_ACCELERATION = 45       # km/h per second when W/UP is pressed
BRAKE_DECELERATION = 80     # km/h per second when S/DOWN is pressed

# -----------------------------
# VEHICLE / FUEL SETTINGS
# -----------------------------
# Easy to extend: add another car type with its own fuel values.
vehicle_types = {
    "standard": {
        "max_fuel": 100.0,
        "base_fuel_usage": 1.5,       # fuel per second while moving
        "gas_fuel_usage": 2.0,        # extra fuel while W/UP is pressed
        "speed_fuel_usage": 2.0,      # extra fuel at high speed
        "slope_fuel_usage": 0.0,      # can be changed later for hills
        "fuel_pickup_amount": 40.0
    }
}
selected_vehicle_type = "standard"
FUEL_CANISTER_DISTANCE = 900          # canister spawns after this distance, not time
FUEL_CANISTER_SIZE = (28, 36)

# Balance settings for events. Bigger distance = fewer objects.
HAZARD_DISTANCE = 1400
OBSTACLE_DISTANCE = 1700
POWERUP_DISTANCE = 1800
TRAFFIC_CHANGE_CHANCE = 0.0015

# Traffic balance. Smaller count = fewer traffic cars.
TRAFFIC_CAR_COUNT = 2
TRAFFIC_SAFE_DISTANCE = 260

# Limit how many objects can be on screen at once.
MAX_HAZARDS = 1
MAX_OBSTACLES = 1
MAX_POWERUPS = 1

# Events scroll slower than the road so they are easier to react to.
EVENT_SCROLL_MULTIPLIER = 0.55
FUEL_SCROLL_MULTIPLIER = 0.70

POWERUP_DURATION = {"nitro": 3.0, "shield": 5.0, "repair": 0.0}

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# -----------------------------
# ROAD LIMITS
# -----------------------------
ROAD_LEFT = 0
ROAD_RIGHT = 400

lanes = [
    ROAD_LEFT + 40,
    (ROAD_LEFT + ROAD_RIGHT) // 2,
    ROAD_RIGHT - 40
]

# -----------------------------
# LEVELS
# -----------------------------
levels = {
    "easy": {
        "road_speed": 80,
        "player_speed": 300,
        "enemy_min": 70,
        "enemy_max": 105
    },
    "medium": {
        "road_speed": 110,
        "player_speed": 340,
        "enemy_min": 95,
        "enemy_max": 145
    },
    "hard": {
        "road_speed": 140,
        "player_speed": 380,
        "enemy_min": 130,
        "enemy_max": 190
    }
}

level_names = ["easy", "medium", "hard"]
selected_level_index = 0
current_level = level_names[selected_level_index]

# -----------------------------
# MENU / GARAGE
# -----------------------------
game_state = "menu"   # menu / garage / settings / playing
menu_options = ["PLAY", "GARAGE", "SETTINGS", "EXIT"]
selected_menu_index = 0
garage_index = 0
sound_on = True
season_names = ["spring", "summer", "autumn", "winter"]
selected_season_index = 1

# -----------------------------
# BEST SCORE SAVE
# -----------------------------
best_score_file = os.path.join(BASE_DIR, "best_score.txt")

def load_best_score():
    if os.path.exists(best_score_file):
        try:
            with open(best_score_file, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_best_score(score):
    try:
        with open(best_score_file, "w") as f:
            f.write(str(score))
    except:
        pass

best_score = load_best_score()

# -----------------------------
# LOAD SOUNDS
# -----------------------------
menu_music_path = os.path.join(SOUNDS_DIR, "menu.mp3")
game_music_path = os.path.join(SOUNDS_DIR, "background.mp3")

crash_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "crash.mp3"))
coin_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "coin.mp3"))

crash_sound.set_volume(0.7)
coin_sound.set_volume(0.7)
pygame.mixer.music.set_volume(0.4)

def update_sound_volume():
    if sound_on:
        pygame.mixer.music.set_volume(0.4)
        crash_sound.set_volume(0.7)
        coin_sound.set_volume(0.7)
    else:
        pygame.mixer.music.set_volume(0)
        crash_sound.set_volume(0)
        coin_sound.set_volume(0)

def safe_sound_play(sound):
    if sound_on:
        sound.play()

def play_menu_music():
    pygame.mixer.music.stop()
    if sound_on:
        pygame.mixer.music.load(menu_music_path)
        pygame.mixer.music.play(-1)

def play_game_music():
    pygame.mixer.music.stop()
    if sound_on:
        pygame.mixer.music.load(game_music_path)
        pygame.mixer.music.play(-1)

# -----------------------------
# LOAD IMAGES
# -----------------------------
season_colors = {
    "spring": (90, 170, 100),
    "summer": (70, 155, 75),
    "autumn": (175, 120, 55),
    "winter": (210, 225, 235)
}

season_road_files = {
    "spring": "Road_spring.jpg",
    "summer": "Road.jpg",
    "autumn": "Road_autumn.jpg",
    "winter": "Road_winter.jpg"
}

def make_tinted_road(base_img, color):
    road = base_img.copy()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((*color, 45))
    road.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return road

def load_road_for_season(season):
    road_path = os.path.join(IMAGES_DIR, season_road_files[season])
    if os.path.exists(road_path):
        img = pygame.image.load(road_path).convert()
        return pygame.transform.scale(img, (WIDTH, HEIGHT))

    base = pygame.image.load(os.path.join(IMAGES_DIR, "Road.jpg")).convert()
    base = pygame.transform.scale(base, (WIDTH, HEIGHT))
    return make_tinted_road(base, season_colors[season])

road_img = load_road_for_season(season_names[selected_season_index])

# player skins
player_skins = []
player_skin_files = [
    "main_car.jpg",
    "NPC1.jpg",
    "NPC2.jpg",
    "NPC3.jpg"
]

for skin_file in player_skin_files:
    img = pygame.image.load(os.path.join(IMAGES_DIR, skin_file)).convert_alpha()
    img = pygame.transform.scale(img, (40, 70))
    player_skins.append(img)

# npc cars
npc_images = []
for i in range(1, 5):
    img = pygame.image.load(os.path.join(IMAGES_DIR, f"NPC{i}.jpg")).convert_alpha()
    img = pygame.transform.scale(img, (40, 70))
    npc_images.append(img)

# coins
coin_images = {
    1: pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGES_DIR, "1coin.jpg")).convert_alpha(), (25, 25)
    ),
    3: pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGES_DIR, "3coin.jpg")).convert_alpha(), (25, 25)
    ),
    5: pygame.transform.scale(
        pygame.image.load(os.path.join(IMAGES_DIR, "5coin.jpg")).convert_alpha(), (25, 25)
    ),
}

# fuel canister image made in code, so no extra asset file is needed
def create_fuel_canister_image():
    img = pygame.Surface(FUEL_CANISTER_SIZE, pygame.SRCALPHA)
    pygame.draw.rect(img, (210, 40, 35), (5, 8, 18, 24), border_radius=4)
    pygame.draw.rect(img, (255, 225, 60), (8, 14, 12, 4), border_radius=2)
    pygame.draw.rect(img, (40, 40, 40), (11, 3, 10, 8), border_radius=2)
    pygame.draw.line(img, (40, 40, 40), (21, 8), (25, 12), 3)
    return img

fuel_canister_img = create_fuel_canister_image()

def create_hazard_image(kind):
    img = pygame.Surface((46, 34), pygame.SRCALPHA)
    if kind == "oil":
        pygame.draw.ellipse(img, (20, 20, 20), (3, 7, 40, 20))
        pygame.draw.ellipse(img, (80, 80, 90), (12, 11, 18, 8))
    else:
        pygame.draw.ellipse(img, (55, 45, 40), (2, 3, 42, 27))
        pygame.draw.ellipse(img, (20, 18, 17), (9, 8, 28, 16))
    return img

def create_obstacle_image(kind):
    img = pygame.Surface((42, 42), pygame.SRCALPHA)
    if kind == "cone":
        pygame.draw.polygon(img, (255, 120, 20), [(21, 3), (7, 35), (35, 35)])
        pygame.draw.rect(img, (245, 245, 245), (13, 22, 16, 5))
    else:
        pygame.draw.rect(img, (180, 40, 35), (4, 12, 34, 18), border_radius=4)
        pygame.draw.rect(img, (245, 245, 245), (9, 15, 24, 5))
    return img

def create_powerup_image(kind):
    colors = {"nitro": (60, 170, 255), "shield": (70, 220, 120), "repair": (255, 80, 90)}
    img = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(img, colors[kind], (16, 16), 15)
    pygame.draw.circle(img, (245, 245, 245), (16, 16), 15, 2)
    icon_font = pygame.font.SysFont("Arial", 18, bold=True)
    symbol = {"nitro": "N", "shield": "S", "repair": "+"}[kind]
    txt = icon_font.render(symbol, True, (20, 20, 20))
    img.blit(txt, (16 - txt.get_width() // 2, 15 - txt.get_height() // 2))
    return img

hazard_images = {"oil": create_hazard_image("oil"), "pothole": create_hazard_image("pothole")}
obstacle_images = {"cone": create_obstacle_image("cone"), "barrier": create_obstacle_image("barrier")}
powerup_images = {kind: create_powerup_image(kind) for kind in ["nitro", "shield", "repair"]}

# -----------------------------
# COIN CHANCE
# -----------------------------
def get_random_coin():
    roll = random.randint(1, 100)
    if roll <= 75:
        return 1   # gray
    elif roll <= 95:
        return 3   # gold
    else:
        return 5   # red

# -----------------------------
# SAFE SPAWN
# -----------------------------
def is_safe_position(x, y, enemies, min_dist=TRAFFIC_SAFE_DISTANCE):
    for e in enemies:
        if abs(e["y"] - y) < min_dist and abs(e["x"] - x) < 10:
            return False
    return True

# -----------------------------
# CREATE ENEMY
# -----------------------------
def create_enemy(level_name):
    level = levels[level_name]
    return {
        "img": random.choice(npc_images),
        "x": random.choice(lanes) - 20,
        "y": random.randint(-1300, -250),
        "target_lane": None,
        "current_speed": 0,
        "max_speed": random.uniform(level["enemy_min"], level["enemy_max"]),
        "acceleration": random.uniform(1.5, 2.5)
    }

# -----------------------------
# RESPAWN COIN
# -----------------------------
def respawn_coin(state):
    while True:
        new_x = random.choice(lanes) - 12
        new_y = random.randint(-300, -100)

        safe = True
        for e in state["enemies"]:
            if abs(e["y"] - new_y) < 80 and abs(e["x"] - new_x) < 20:
                safe = False
                break

        if safe:
            state["coin_x"] = new_x
            state["coin_y"] = new_y
            state["coin_value"] = get_random_coin()
            break

# -----------------------------
# FUEL SYSTEM
# -----------------------------
def create_fuel_canister():
    return {
        "x": random.choice(lanes) - FUEL_CANISTER_SIZE[0] // 2,
        "y": random.randint(-450, -150),
        "active": True
    }

def respawn_fuel_canister(state):
    state["fuel_canister"] = create_fuel_canister()
    state["distance_since_fuel"] = 0.0

def update_fuel(state, dt, gas_pressed, speed_ratio):
    car = vehicle_types[state["vehicle_type"]]
    usage = car["base_fuel_usage"]
    usage += car["speed_fuel_usage"] * speed_ratio
    usage += car["slope_fuel_usage"]
    if gas_pressed:
        usage += car["gas_fuel_usage"]

    state["fuel"] -= usage * dt
    state["fuel"] = max(0.0, min(state["max_fuel"], state["fuel"]))

    if state["fuel"] <= 0:
        pygame.mixer.music.stop()
        state["game_over"] = True
        state["game_over_reason"] = "OUT OF FUEL"
        update_best_score()

def add_fuel(state):
    car = vehicle_types[state["vehicle_type"]]
    state["fuel"] = min(state["max_fuel"], state["fuel"] + car["fuel_pickup_amount"])

def draw_fuel_bar(surface, x, y, width, height, fuel, max_fuel):
    ratio = 0 if max_fuel <= 0 else fuel / max_fuel
    pygame.draw.rect(surface, (35, 35, 35), (x, y, width, height), border_radius=6)
    pygame.draw.rect(surface, (230, 230, 230), (x, y, width, height), 2, border_radius=6)
    inner_width = int((width - 4) * ratio)
    if inner_width > 0:
        pygame.draw.rect(surface, (235, 185, 55), (x + 2, y + 2, inner_width, height - 4), border_radius=5)

# -----------------------------
# HAZARDS / OBSTACLES / POWER-UPS
# -----------------------------
def create_lane_object(kind_group):
    lane_x = random.choice(lanes)
    if kind_group == "hazard":
        kind = random.choice(["oil", "pothole"]); size = (46, 34)
    elif kind_group == "obstacle":
        kind = random.choice(["cone", "barrier"]); size = (42, 42)
    else:
        kind = random.choice(["nitro", "shield", "repair"]); size = (32, 32)
    return {"kind": kind, "x": lane_x - size[0] // 2, "y": random.randint(-520, -140), "size": size}

def spawn_distance_objects(state):
    if state["distance_since_hazard"] >= HAZARD_DISTANCE:
        if len(state["hazards"]) < MAX_HAZARDS:
            state["hazards"].append(create_lane_object("hazard"))
        state["distance_since_hazard"] = 0.0

    if state["distance_since_obstacle"] >= OBSTACLE_DISTANCE:
        if len(state["obstacles"]) < MAX_OBSTACLES:
            state["obstacles"].append(create_lane_object("obstacle"))
        state["distance_since_obstacle"] = 0.0

    if state["distance_since_powerup"] >= POWERUP_DISTANCE:
        if len(state["powerups"]) < MAX_POWERUPS:
            state["powerups"].append(create_lane_object("powerup"))
        state["distance_since_powerup"] = 0.0

def update_dynamic_traffic(state, dt):
    for enemy in state["enemies"]:
        if random.random() < TRAFFIC_CHANGE_CHANCE:
            possible = [l - 20 for l in lanes if abs((l - 20) - enemy["x"]) > 5]
            random.shuffle(possible)
            for lane_x in possible:
                if all(abs(e["x"] - lane_x) > 5 or abs(e["y"] - enemy["y"]) > 120 for e in state["enemies"] if e != enemy):
                    enemy["target_lane"] = lane_x; break
        enemy["max_speed"] = max(65, min(220, enemy["max_speed"] + random.uniform(-3, 3) * dt))

def update_scrolling_objects(items, road_speed):
    for item in items[:]:
        item["y"] += road_speed
        if item["y"] > HEIGHT + 60:
            items.remove(item)

def use_shield_or_game_over(state, reason="CRASH"):
    if state["shield_time"] > 0:
        state["shield_time"] = 0
        return False
    safe_sound_play(crash_sound)
    pygame.mixer.music.stop()
    state["game_over"] = True
    state["game_over_reason"] = reason
    update_best_score()
    return True

def collect_powerup(state, kind):
    if kind == "nitro":
        state["nitro_time"] = POWERUP_DURATION["nitro"]
    elif kind == "shield":
        state["shield_time"] = POWERUP_DURATION["shield"]
    elif kind == "repair":
        add_fuel(state)

def draw_powerup_status(surface, state):
    y = 205
    if state["nitro_time"] > 0:
        txt = small_font.render(f"Nitro: {state['nitro_time']:.1f}s", True, (120, 210, 255))
        surface.blit(txt, (10, y)); y += 24
    if state["shield_time"] > 0:
        txt = small_font.render(f"Shield: {state['shield_time']:.1f}s", True, (120, 255, 150))
        surface.blit(txt, (10, y))

# -----------------------------
# RESET GAME
# -----------------------------
def reset_game(level_name):
    enemies = []

    for _ in range(TRAFFIC_CAR_COUNT):
        while True:
            e = create_enemy(level_name)
            if is_safe_position(e["x"], e["y"], enemies):
                enemies.append(e)
                break

    car = vehicle_types[selected_vehicle_type]

    return {
        "player_x": lanes[1] - 20,
        "player_y": HEIGHT - 100,

        "enemies": enemies,

        "coin_value": get_random_coin(),
        "coin_x": random.choice(lanes) - 12,
        "coin_y": -200,
        "coin_speed": 5,

        "fuel": car["max_fuel"],
        "max_fuel": car["max_fuel"],
        "vehicle_type": selected_vehicle_type,
        "fuel_canister": None,
        "hazards": [],
        "obstacles": [],
        "powerups": [],
        "nitro_time": 0.0,
        "shield_time": 0.0,
        "distance": 0.0,
        "distance_since_fuel": 0.0,
        "distance_since_hazard": 0.0,
        "distance_since_obstacle": 0.0,
        "distance_since_powerup": 0.0,

        "road_y1": 0.0,
        "road_y2": -HEIGHT,

        "coins": 0,
        "score": 0,
        "game_over": False,
        "game_over_reason": "",
        "level": level_name,
        "skin_index": garage_index,
        "season": season_names[selected_season_index],
        "speed": 0
    }

state = None

font = pygame.font.SysFont("Arial", 24)
game_over_font = pygame.font.SysFont("Arial", 40)
title_font = pygame.font.SysFont("Arial", 50)
menu_font = pygame.font.SysFont("Arial", 32)
small_font = pygame.font.SysFont("Arial", 22)

def update_best_score():
    global best_score, state
    if state["score"] > best_score:
        best_score = state["score"]
        save_best_score(best_score)

# =====================================
# LOOP
# =====================================
play_menu_music()
running = True

while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "menu":
                if event.key == pygame.K_UP:
                    selected_menu_index = (selected_menu_index - 1) % len(menu_options)

                elif event.key == pygame.K_DOWN:
                    selected_menu_index = (selected_menu_index + 1) % len(menu_options)

                elif event.key == pygame.K_LEFT:
                    if menu_options[selected_menu_index] == "PLAY":
                        selected_level_index = (selected_level_index - 1) % len(level_names)
                        current_level = level_names[selected_level_index]

                elif event.key == pygame.K_RIGHT:
                    if menu_options[selected_menu_index] == "PLAY":
                        selected_level_index = (selected_level_index + 1) % len(level_names)
                        current_level = level_names[selected_level_index]

                elif event.key == pygame.K_RETURN:
                    selected_option = menu_options[selected_menu_index]

                    if selected_option == "PLAY":
                        state = reset_game(current_level)
                        game_state = "playing"
                        play_game_music()

                    elif selected_option == "GARAGE":
                        game_state = "garage"

                    elif selected_option == "SETTINGS":
                        game_state = "settings"

                    elif selected_option == "EXIT":
                        running = False

            elif game_state == "garage":
                if event.key == pygame.K_LEFT:
                    garage_index = (garage_index - 1) % len(player_skins)

                elif event.key == pygame.K_RIGHT:
                    garage_index = (garage_index + 1) % len(player_skins)

                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    game_state = "menu"

            elif game_state == "settings":
                if event.key == pygame.K_LEFT:
                    selected_season_index = (selected_season_index - 1) % len(season_names)
                    road_img = load_road_for_season(season_names[selected_season_index])

                elif event.key == pygame.K_RIGHT:
                    selected_season_index = (selected_season_index + 1) % len(season_names)
                    road_img = load_road_for_season(season_names[selected_season_index])

                elif event.key == pygame.K_s:
                    sound_on = not sound_on
                    update_sound_volume()
                    if sound_on:
                        play_menu_music()
                    else:
                        pygame.mixer.music.stop()

                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    game_state = "menu"

            elif game_state == "playing":
                if state["game_over"] and event.key == pygame.K_r:
                    state = reset_game(state["level"])
                    play_game_music()

                elif state["game_over"] and event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                    state = None
                    play_menu_music()

    keys = pygame.key.get_pressed()

    if game_state == "playing" and not state["game_over"]:

        player_speed = levels[state["level"]]["player_speed"]

        # SMOOTH SPEED UP / BRAKE
        # Speed grows gradually and never goes higher than 200 km/h.
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            state["speed"] -= BRAKE_DECELERATION * dt
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            state["speed"] += GAS_ACCELERATION * dt
        else:
            state["speed"] += AUTO_ACCELERATION * dt

        state["speed"] = max(0, min(MAX_SPEED_KMH, state["speed"]))
        road_base_speed = state["speed"]
        speed_multiplier = max(0.35, state["speed"] / MAX_SPEED_KMH)
        gas_pressed = keys[pygame.K_w] or keys[pygame.K_UP]

        if state["nitro_time"] > 0:
            state["nitro_time"] = max(0, state["nitro_time"] - dt)
            state["speed"] = min(MAX_SPEED_KMH, state["speed"] + 65 * dt)
            speed_multiplier = min(1.25, speed_multiplier + 0.35)
        if state["shield_time"] > 0:
            state["shield_time"] = max(0, state["shield_time"] - dt)

        # FUEL: usage depends on time, speed and gas.
        update_fuel(state, dt, gas_pressed, state["speed"] / MAX_SPEED_KMH)

        # DISTANCE: canisters spawn by distance, not by time.
        distance_step = road_base_speed * dt
        state["distance"] += distance_step
        state["distance_since_fuel"] += distance_step
        state["distance_since_hazard"] += distance_step
        state["distance_since_obstacle"] += distance_step
        state["distance_since_powerup"] += distance_step
        if state["fuel_canister"] is None and state["distance_since_fuel"] >= FUEL_CANISTER_DISTANCE:
            respawn_fuel_canister(state)
        spawn_distance_objects(state)

        # Car turns a little faster as the game speed grows.
        player_speed *= 0.85 + speed_multiplier

        # PLAYER MOVE
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            state["player_x"] -= player_speed * dt * 0.5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            state["player_x"] += player_speed * dt * 0.5

        # ROAD LIMIT
        if state["player_x"] < ROAD_LEFT or state["player_x"] > ROAD_RIGHT - 40:
            use_shield_or_game_over(state, "OFF ROAD")

        # ROAD SCROLL
        road_speed = road_base_speed * dt
        state["road_y1"] += road_speed
        state["road_y2"] += road_speed

        if state["road_y1"] >= HEIGHT:
            state["road_y1"] = -HEIGHT
        if state["road_y2"] >= HEIGHT:
            state["road_y2"] = -HEIGHT

        # DYNAMIC TRAFFIC
        update_dynamic_traffic(state, dt)

        # ENEMIES
        for enemy in state["enemies"]:
            target_speed = enemy["max_speed"] * speed_multiplier

            for other in state["enemies"]:
                if other == enemy:
                    continue

                same_lane = abs(enemy["x"] - other["x"]) < 5
                in_front = other["y"] > enemy["y"]
                close = other["y"] - enemy["y"] < 120

                if same_lane and in_front and close:
                    target_speed = other["current_speed"] * 0.8

                    if enemy["target_lane"] is None:
                        possible = [l for l in lanes if abs((l - 20) - enemy["x"]) > 5]

                        for lane in possible:
                            lane_x = lane - 20
                            free = True
                            for e in state["enemies"]:
                                if abs(e["x"] - lane_x) < 5 and abs(e["y"] - enemy["y"]) < 120:
                                    free = False
                                    break
                            if free:
                                enemy["target_lane"] = lane_x
                                break
                    break

            enemy["current_speed"] += (target_speed - enemy["current_speed"]) * enemy["acceleration"] * dt
            enemy["y"] += enemy["current_speed"] * dt

            if enemy["target_lane"] is not None:
                enemy["x"] += (enemy["target_lane"] - enemy["x"]) * 4 * dt
                if abs(enemy["target_lane"] - enemy["x"]) < 2:
                    enemy["target_lane"] = None

            if enemy["y"] > HEIGHT:
                while True:
                    new_enemy = create_enemy(state["level"])
                    if is_safe_position(new_enemy["x"], new_enemy["y"], state["enemies"], TRAFFIC_SAFE_DISTANCE):
                        enemy.update(new_enemy)
                        state["score"] += 1
                        update_best_score()
                        break

        # COIN
        state["coin_y"] += state["coin_speed"] * 60 * dt * speed_multiplier

        if state["coin_y"] > HEIGHT:
            respawn_coin(state)

        # FUEL CANISTER
        if state["fuel_canister"] is not None:
            state["fuel_canister"]["y"] += road_speed * FUEL_SCROLL_MULTIPLIER
            if state["fuel_canister"]["y"] > HEIGHT:
                state["fuel_canister"] = None

        event_scroll_speed = road_speed * EVENT_SCROLL_MULTIPLIER
        update_scrolling_objects(state["hazards"], event_scroll_speed)
        update_scrolling_objects(state["obstacles"], event_scroll_speed)
        update_scrolling_objects(state["powerups"], event_scroll_speed)

        # COLLISIONS
        player_rect = pygame.Rect(state["player_x"], state["player_y"], 40, 70)

        for enemy in state["enemies"]:
            enemy_rect = pygame.Rect(enemy["x"], enemy["y"], 40, 70)
            if player_rect.colliderect(enemy_rect):
                use_shield_or_game_over(state, "CRASH")

        coin_rect = pygame.Rect(state["coin_x"], state["coin_y"], 25, 25)
        if player_rect.colliderect(coin_rect):
            safe_sound_play(coin_sound)
            state["coins"] += state["coin_value"]
            respawn_coin(state)

        if state["fuel_canister"] is not None:
            fuel_rect = pygame.Rect(
                state["fuel_canister"]["x"],
                state["fuel_canister"]["y"],
                FUEL_CANISTER_SIZE[0],
                FUEL_CANISTER_SIZE[1]
            )
            if player_rect.colliderect(fuel_rect):
                safe_sound_play(coin_sound)
                add_fuel(state)
                state["fuel_canister"] = None

        for hazard in state["hazards"][:]:
            rect = pygame.Rect(hazard["x"], hazard["y"], hazard["size"][0], hazard["size"][1])
            if player_rect.colliderect(rect):
                state["hazards"].remove(hazard)
                if hazard["kind"] == "oil":
                    state["player_x"] += random.choice([-1, 1]) * 35
                    state["speed"] *= 0.9
                else:
                    state["speed"] *= 0.65

        for obstacle in state["obstacles"][:]:
            rect = pygame.Rect(obstacle["x"], obstacle["y"], obstacle["size"][0], obstacle["size"][1])
            if player_rect.colliderect(rect):
                state["obstacles"].remove(obstacle)
                use_shield_or_game_over(state, "ROAD OBSTACLE")

        for powerup in state["powerups"][:]:
            rect = pygame.Rect(powerup["x"], powerup["y"], powerup["size"][0], powerup["size"][1])
            if player_rect.colliderect(rect):
                safe_sound_play(coin_sound)
                collect_powerup(state, powerup["kind"])
                state["powerups"].remove(powerup)

    # DRAW
    screen.fill((20, 20, 20))

    if game_state == "menu":
        screen.fill((18, 24, 32))
        pygame.draw.rect(screen, (35, 45, 60), (45, 80, WIDTH - 90, 450), border_radius=22)
        title_text = title_font.render("RACER", True, (245, 245, 245))
        info_text = small_font.render("UP/DOWN menu  LEFT/RIGHT level  ENTER choose", True, (170, 180, 190))
        level_info = small_font.render(f"Level: {current_level.upper()}   Map: {season_names[selected_season_index].upper()}", True, (220, 220, 220))
        sound_info = small_font.render(f"Sound: {'ON' if sound_on else 'OFF'}", True, (220, 220, 220))
        best_menu_text = small_font.render(f"Best score: {best_score}", True, (220, 220, 220))

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 115))

        for i, option in enumerate(menu_options):
            selected = i == selected_menu_index
            color = (255, 230, 70) if selected else (245, 245, 245)
            if selected:
                pygame.draw.rect(screen, (55, 70, 90), (95, 230 + i * 55, 210, 42), border_radius=14)
            option_text = menu_font.render(option, True, color)
            screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, 235 + i * 55))

        screen.blit(level_info, (WIDTH // 2 - level_info.get_width() // 2, 475))
        screen.blit(sound_info, (WIDTH // 2 - sound_info.get_width() // 2, 500))
        screen.blit(best_menu_text, (WIDTH // 2 - best_menu_text.get_width() // 2, 525))
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 565))

    elif game_state == "garage":
        garage_title = title_font.render("GARAGE", True, (255, 255, 255))
        garage_info = small_font.render("LEFT/RIGHT - change skin   ENTER/ESC - back", True, (200, 200, 200))
        skin_name = small_font.render(f"Skin {garage_index + 1}", True, (255, 255, 0))

        screen.blit(garage_title, (WIDTH // 2 - garage_title.get_width() // 2, 120))
        screen.blit(player_skins[garage_index], (WIDTH // 2 - 20, HEIGHT // 2 - 35))
        screen.blit(skin_name, (WIDTH // 2 - skin_name.get_width() // 2, HEIGHT // 2 + 70))
        screen.blit(garage_info, (WIDTH // 2 - garage_info.get_width() // 2, 620))

    elif game_state == "settings":
        screen.fill((18, 24, 32))
        pygame.draw.rect(screen, (35, 45, 60), (45, 90, WIDTH - 90, 400), border_radius=22)

        settings_title = title_font.render("SETTINGS", True, (255, 255, 255))
        sound_text = menu_font.render(f"Sound: {'ON' if sound_on else 'OFF'}", True, (255, 230, 70))
        map_text = menu_font.render(f"Map: {season_names[selected_season_index].upper()}", True, (255, 255, 255))
        settings_info1 = small_font.render("Press S to turn sound ON/OFF", True, (200, 200, 200))
        settings_info2 = small_font.render("LEFT/RIGHT to change map", True, (200, 200, 200))
        settings_info3 = small_font.render("ENTER/ESC - back", True, (200, 200, 200))

        screen.blit(settings_title, (WIDTH // 2 - settings_title.get_width() // 2, 125))
        screen.blit(sound_text, (WIDTH // 2 - sound_text.get_width() // 2, 240))
        screen.blit(map_text, (WIDTH // 2 - map_text.get_width() // 2, 300))
        screen.blit(settings_info1, (WIDTH // 2 - settings_info1.get_width() // 2, 390))
        screen.blit(settings_info2, (WIDTH // 2 - settings_info2.get_width() // 2, 420))
        screen.blit(settings_info3, (WIDTH // 2 - settings_info3.get_width() // 2, 450))

    elif game_state == "playing":
        screen.blit(road_img, (0, int(state["road_y1"])))
        screen.blit(road_img, (0, int(state["road_y2"])))

        screen.blit(player_skins[state["skin_index"]], (state["player_x"], state["player_y"]))

        for enemy in state["enemies"]:
            screen.blit(enemy["img"], (enemy["x"], enemy["y"]))

        coin_img = coin_images[state["coin_value"]]
        screen.blit(coin_img, (state["coin_x"], state["coin_y"]))

        if state["fuel_canister"] is not None:
            screen.blit(fuel_canister_img, (state["fuel_canister"]["x"], state["fuel_canister"]["y"]))

        for hazard in state["hazards"]:
            screen.blit(hazard_images[hazard["kind"]], (hazard["x"], hazard["y"]))
        for obstacle in state["obstacles"]:
            screen.blit(obstacle_images[obstacle["kind"]], (obstacle["x"], obstacle["y"]))
        for powerup in state["powerups"]:
            screen.blit(powerup_images[powerup["kind"]], (powerup["x"], powerup["y"]))

        if state["shield_time"] > 0:
            pygame.draw.circle(screen, (90, 230, 130), (int(state["player_x"] + 20), int(state["player_y"] + 35)), 45, 3)

        # UI
        score_text = font.render(f"Score: {state['score']}", True, (255, 255, 255))
        coins_text = font.render(f"Coins: {state['coins']}", True, (255, 255, 255))
        level_text = font.render(f"Level: {state['level'].upper()}", True, (255, 255, 255))
        season_text = font.render(f"Map: {state['season'].upper()}", True, (255, 255, 255))
        speed_text = font.render(f"Speed: {int(state['speed'])} km/h", True, (255, 255, 255))
        fuel_text = font.render(f"Fuel: {int(state['fuel'])}/{int(state['max_fuel'])}", True, (255, 255, 255))
        best_text = font.render(f"Best: {best_score}", True, (255, 255, 255))

        screen.blit(score_text, (10, 10))
        screen.blit(coins_text, (WIDTH - coins_text.get_width() - 10, 10))
        screen.blit(level_text, (10, 45))
        screen.blit(season_text, (10, 80))
        screen.blit(speed_text, (10, 115))
        screen.blit(fuel_text, (10, 150))
        draw_fuel_bar(screen, 10, 180, 145, 18, state["fuel"], state["max_fuel"])
        draw_powerup_status(screen, state)
        screen.blit(best_text, (WIDTH - best_text.get_width() - 10, 45))

        if state["game_over"]:
            text1 = game_over_font.render("GAME OVER", True, (255, 0, 0))
            reason = state.get("game_over_reason", "")
            text_reason = small_font.render(reason, True, (255, 230, 70)) if reason else None
            text2 = small_font.render("Press R to restart", True, (255, 255, 255))
            text3 = small_font.render("Press ESC for menu", True, (255, 255, 255))

            screen.blit(text1, (
                WIDTH // 2 - text1.get_width() // 2,
                HEIGHT // 2 - 80
            ))
            if text_reason:
                screen.blit(text_reason, (
                    WIDTH // 2 - text_reason.get_width() // 2,
                    HEIGHT // 2 - 35
                ))
            screen.blit(text2, (
                WIDTH // 2 - text2.get_width() // 2,
                HEIGHT // 2 + 5
            ))
            screen.blit(text3, (
                WIDTH // 2 - text3.get_width() // 2,
                HEIGHT // 2 + 40
            ))

    pygame.display.update()

pygame.quit()
sys.exit()