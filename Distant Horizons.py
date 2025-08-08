import pygame
import math
import sys
import os
import random

TIT_center_x = 500
TIT_center_y = 200

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(base_path)

pygame.init()

FPS = 60
TITLE = "Distant Horizons"
BG = (8, 0, 41)

try:
    pixel_font = pygame.font.Font(
        r"D:\\Visual studio\\Projects (VSC)\\Distant Horizons\\Assets\\PressStart2P-Regular.ttf", 26)
except:
    pixel_font = pygame.font.SysFont("Verdana", 26)

screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

def load_sprite(path):
    return pygame.image.load(os.path.join(base_path, path)).convert_alpha()

title = load_sprite("Assets/title screen.png")
text_surf = pixel_font.render("Press any key to start", True, (100, 100, 255))
start1 = load_sprite("Assets/start1.png")
start3 = load_sprite("Assets/start3.png")
star_img = load_sprite("Assets/star.png")

ISS_arrow = pygame.transform.scale(load_sprite("Assets/arrow.png"), (100, 100))
AST_arrow = pygame.transform.scale(load_sprite("Assets/arrow.png"), (100, 100))

# In game assets
SpaceStation = pygame.transform.scale(load_sprite("Assets/SpaceStation_ent.png"), (600, 600))
Falcon = pygame.transform.scale(load_sprite("Assets/Falcon.png"), (100, 100))
Monk = pygame.transform.scale(load_sprite("Assets/Monk.png"), (100, 100))
Shield = pygame.transform.scale(load_sprite("Assets/Shield.png"), (100, 100))



Hervinite = [
    pygame.transform.scale(load_sprite("Assets/Asteroids/Hervinite/Hervinite1.png"), (150, 150)),
    pygame.transform.scale(load_sprite("Assets/Asteroids/Hervinite/Hervinite2.png"), (150, 150)),
    pygame.transform.scale(load_sprite("Assets/Asteroids/Hervinite/Hervinite3.png"), (150, 150)),
    pygame.transform.scale(load_sprite("Assets/Asteroids/Hervinite/Hervinite4.png"), (150, 150)),
    pygame.transform.scale(load_sprite("Assets/Asteroids/Hervinite/Hervinite5.png"), (150, 150))
]



class Star:
    def __init__(self):
        self.x = random.randint(-100, 1100)
        self.y = random.randint(-100, 700)  # Allow stars to spawn above and below the screen
        self.speed = random.uniform(0.2, 1.2)
        self.angle = random.uniform(0, 360)
        self.size = random.randint(5, 25)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-0.3, 0.3)
        self.image_orig = pygame.transform.scale(star_img, (self.size, self.size))

    def update(self, dx=0, dy=0, title_screen_visible=False, player_is_moving=False):
        if not title_screen_visible:
            self.x += dx
            self.y += dy
        elif player_is_moving:
            self.x += dx * 0.3
            self.y += dy * 0.3


        # Always rotate stars regardless of movement
        self.rotation += self.rotation_speed

        # Respawn stars when they leave the screen
        if self.x > 1100 or self.x < -100 or self.y > 700 or self.y < -100:
            self.__init__()

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image_orig, self.rotation)
        rect = rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(rotated_image, rect)

stars = [Star() for _ in range(60)]

def fade_in_out(image, fade_duration=2000, hold_duration=1000):
    start_time = pygame.time.get_ticks()
    image = pygame.transform.scale(image, (600, 600))

    fade_in_time = fade_duration // 2
    fade_out_time = fade_duration // 2
    total_time = fade_in_time + hold_duration + fade_out_time

    running = True
    while running:
        dt = clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time

        if elapsed > total_time:
            running = False
            continue

        screen.fill((0, 0, 0))

        if elapsed < fade_in_time:
            alpha = int((elapsed / fade_in_time) * 255)
        elif elapsed < fade_in_time + hold_duration:
            alpha = 255
        else:
            alpha = int(((total_time - elapsed) / fade_out_time) * 255)

        faded_image = image.copy()
        faded_image.set_alpha(alpha)
        rect = faded_image.get_rect(center=(500, 300))
        screen.blit(faded_image, rect)
        pygame.display.flip()

def fade_to_black_then_tutorial(screen, clock, FPS, tutorial_callback):
    fade_surface = pygame.Surface((1000, 600))
    fade_surface.fill((0, 0, 0))

    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    tutorial_callback()

    for alpha in range(255, -1, -5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

fade_in_out(start1)
fade_in_out(start3)

# Place the space station so its bottom-right corner is at the middle of the right side of the map
# Map size: 5000x5000, SpaceStation size: 600x600
# Middle right side: (5000, 2500)
# So, top-left of station: (5000 - 600, 2500 - 600) = (4400, 1900)
SpaceStation_POS = (4400, 2400)  # 300 = 600//2

class PlayerShip:
    def __init__(self):
        self.image = Falcon
        self.x = SpaceStation_POS[0] - 120
        self.y = SpaceStation_POS[1] + 300
        self.angle = 90
        self.vel_x = 0
        self.vel_y = 0

    def handle_input(self, keys):
        rotate_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        rotate_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        thrust_forward = keys[pygame.K_UP] or keys[pygame.K_w]
        thrust_backward = keys[pygame.K_DOWN] or keys[pygame.K_s]

        if rotate_left:
            self.angle += 3
        if rotate_right:
            self.angle -= 3
        if thrust_forward:
            rad = math.radians(self.angle)
            self.vel_x += -math.sin(rad) * 0.15
            self.vel_y += -math.cos(rad) * 0.15
        if thrust_backward:
            rad = math.radians(self.angle)
            self.vel_x -= -math.sin(rad) * 0.07
            self.vel_y -= -math.cos(rad) * 0.07

    def update(self):
        # Apply friction
        self.vel_x *= 0.995
        self.vel_y *= 0.995

        # Predict new position
        new_x = self.x + self.vel_x
        new_y = self.y + self.vel_y

        # Handle x-axis wall collisions
        if new_x < 0:
            self.x = 0
            self.vel_x = 0
        elif new_x > 5000:
            self.x = 5000
            self.vel_x = 0
        else:
            self.x = new_x

        # Handle y-axis wall collisions
        if new_y < 0:
            self.y = 0
            self.vel_y = 0
        elif new_y > 5000:
            self.y = 5000
            self.vel_y = 0
        else:
            self.y = new_y

    def draw(self, surf):
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(500, 300))
        surf.blit(rotated, rect)


# Asteroid class for stationary, slowly rotating asteroids
class Asteroid:
    def __init__(self):
        self.image_orig = random.choice(Hervinite)
        self.x = random.randint(0, 5000)
        self.y = random.randint(0, 5000)
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-0.2, 0.2)

    def update(self):
        self.angle = (self.angle + self.rotation_speed) % 360

    def draw(self, surf, cam_x, cam_y):
        rotated = pygame.transform.rotate(self.image_orig, self.angle)
        rect = rotated.get_rect(center=(self.x - cam_x + 75, self.y - cam_y + 75))  # 75 = half of 150
        surf.blit(rotated, rect)

asteroids = [Asteroid() for _ in range(10)]

MAP_WIDTH = 5000
MAP_HEIGHT = 5000
def draw_space_world(player):
    cam_x = player.x - 500
    cam_y = player.y - 300

    world_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)

    # Fill screen with black — this is your base color outside the world
    screen.fill((0, 0, 0))

    # === STEP 1: Create a temp surface just for the visible map area ===
    map_surface = pygame.Surface((1000, 600))
    map_surface.fill((5, 0, 20))  # starry background color

    # === STEP 2: Only update/draw stars if camera is in bounds ===
    moving = abs(player.vel_x) > 0.01 or abs(player.vel_y) > 0.01
    dx = -player.vel_x * 0.2 if moving and 0 < cam_x < MAP_WIDTH - 1000 else 0
    dy = -player.vel_y * 0.2 if moving and 0 < cam_y < MAP_HEIGHT - 600 else 0

    for star in stars:
        star.update(dx=dx, dy=dy)
        star.draw(map_surface)

    # === STEP 3: Blit only the part of map_surface that overlaps the world ===
    map_rect = pygame.Rect(cam_x, cam_y, 1000, 600)
    visible_rect = map_rect.clip(world_rect)

    if visible_rect.width > 0 and visible_rect.height > 0:
        # Source rect on map_surface
        src_rect = pygame.Rect(visible_rect.x - cam_x, visible_rect.y - cam_y, visible_rect.width, visible_rect.height)
        # Destination position on screen
        dest_pos = (visible_rect.x - cam_x, visible_rect.y - cam_y)
        screen.blit(map_surface, dest_pos, src_rect)

    # === STEP 4: Only draw game objects if they are inside the map ===
    if world_rect.collidepoint(SpaceStation_POS):
        screen.blit(SpaceStation, (SpaceStation_POS[0] - cam_x, SpaceStation_POS[1] - cam_y))

    for asteroid in asteroids:
        if world_rect.collidepoint(asteroid.x, asteroid.y):
            asteroid.update()
            asteroid.draw(screen, cam_x, cam_y)

    player.draw(screen)

    # === STEP 5: Draw black mask over out-of-bounds areas (failsafe) ===
    if cam_x < 0:
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, -cam_x, 600))
    if cam_y < 0:
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, 1000, -cam_y))
    if cam_x + 1000 > MAP_WIDTH:
        over_x = cam_x + 1000 - MAP_WIDTH
        pygame.draw.rect(screen, (0, 0, 0), (1000 - over_x, 0, over_x, 600))
    if cam_y + 600 > MAP_HEIGHT:
        over_y = cam_y + 600 - MAP_HEIGHT
        pygame.draw.rect(screen, (0, 0, 0), (0, 600 - over_y, 1000, over_y))
    print(f"cam_x={cam_x}, cam_y={cam_y}")

        # === STEP 6: Draw arrow pointing to space station ===
    dx = SpaceStation_POS[0] - player.x
    dy = SpaceStation_POS[1] - player.y
    angle_rad = math.atan2(-dy, dx)  # Invert y for screen coordinate system
    angle_deg = math.degrees(angle_rad)

    
        # === STEP 6: Draw arrow pointing to space station ===

    station_center_x = SpaceStation_POS[0] + 600 // 2
    station_center_y = SpaceStation_POS[1] + 600 // 2

    dx = station_center_x - player.x
    dy = player.y - station_center_y  # Invert y for screen coordinate system
    angle_rad = math.atan2(dy, dx)  # Negative dy because screen y is downward
    angle_deg = math.degrees(angle_rad) - 90  # Adjust so arrow points correctly
    print(f"Arrow angle: {angle_deg:.2f} degrees")

    rotated_arrow = pygame.transform.rotate(ISS_arrow, angle_deg)
    arrow_rect = rotated_arrow.get_rect(center=(980, 20))  # Adjust screen position if needed
    screen.blit(rotated_arrow, arrow_rect)



player = PlayerShip()
title_screen_visible = True

def tutorial_scene():
    global title_screen_visible
    title_screen_visible = False
    run = True
    player = PlayerShip()
    while run:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        screen.fill((5, 0, 20))
        

        draw_space_world(player)
        pygame.display.flip()
        print(f"vel_x: {player.vel_x:.2f}, vel_y: {player.vel_y:.2f}")


run = True
while run:
    dt = clock.tick(FPS)
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            run = False

    screen.fill(BG)

    # On the title screen, stars move normally (no parallax)
    for star in stars:
        star.update()
        star.draw(screen)
    

    player_is_moving = abs(player.vel_x) > 0.01 or abs(player.vel_y) > 0.01
    dx = -player.vel_x * 0.2 if player_is_moving else 0
    dy = -player.vel_y * 0.2 if player_is_moving else 0
    for star in stars:
        star.update(dx=dx, dy=dy, title_screen_visible=title_screen_visible, player_is_moving=player_is_moving)
        star.draw(screen)


    scale_factor = 1 + 0.05 * math.sin(current_time * 0.0015)
    rotation_angle = 2 * math.sin(current_time * 0.0012)
    base_title = pygame.transform.scale(title, (400, 400))
    scaled_title = pygame.transform.smoothscale(base_title, (int(400 * scale_factor), int(400 * scale_factor)))
    rotated_title = pygame.transform.rotate(scaled_title, rotation_angle)
    title_rect = rotated_title.get_rect(center=(TIT_center_x, TIT_center_y))
    screen.blit(rotated_title, title_rect)

    alpha = int((math.sin(current_time * 0.002) + 1) * 127.5)
    text_copy = text_surf.copy()
    text_copy.set_alpha(alpha)
    text_rect = text_copy.get_rect(center=(TIT_center_x, TIT_center_y + 250))
    screen.blit(text_copy, text_rect)

    

    pygame.display.flip()

fade_to_black_then_tutorial(screen, clock, FPS, tutorial_scene)
pygame.quit()
