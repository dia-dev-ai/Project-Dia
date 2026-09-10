import math
import random
import pygame
import numpy as np

pygame.init()

# =========================================================
# WINDOW
# =========================================================

WIDTH, HEIGHT = 1100, 700

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

pygame.display.set_caption("D.I.A. — Core Visualizer")

clock = pygame.time.Clock()

# =========================================================
# CORE SETTINGS
# =========================================================

PARTICLE_COUNT = 5000
SPHERE_RADIUS = 250

# D.I.A. amber/golden identity
CORE_COLOR = np.array([255, 190, 55], dtype=np.float32)

BACKGROUND = (3, 4, 7)

# =========================================================
# PARTICLE GENERATION
# =========================================================

particles = []

for _ in range(PARTICLE_COUNT):

    theta = random.uniform(0, math.tau)
    phi = math.acos(random.uniform(-1, 1))

    # Natural volume distribution
    radius = SPHERE_RADIUS * (random.random() ** (1 / 3))

    x = radius * math.sin(phi) * math.cos(theta)

    y = radius * math.cos(phi)

    z = radius * math.sin(phi) * math.sin(theta)

    particles.append([x, y, z])


particles = np.array(particles, dtype=np.float32)

# Each particle gets its own movement phase
particle_phase = np.random.uniform(0, math.tau, PARTICLE_COUNT).astype(np.float32)

particle_speed = np.random.uniform(0.6, 1.4, PARTICLE_COUNT).astype(np.float32)

# =========================================================
# ROTATION
# =========================================================

rotation_x = 0.0
rotation_y = 0.0

auto_rotation = True

mouse_down = False
last_mouse = (0, 0)

# =========================================================
# TIME
# =========================================================

time_value = 0.0

# =========================================================
# SIMULATED AUDIO
# =========================================================

simulating_voice = False

voice_intensity = 0.0
target_intensity = 0.0


# =========================================================
# DRAW VISUALIZER
# =========================================================


def draw_visualizer():

    global time_value
    global voice_intensity

    screen.fill(BACKGROUND)

    # -----------------------------------------------------
    # NATURAL BREATHING
    # -----------------------------------------------------

    breathing = math.sin(time_value * 1.7) * 0.035 + math.sin(time_value * 0.63) * 0.018

    # -----------------------------------------------------
    # SIMULATED VOICE RESPONSE
    # -----------------------------------------------------

    breathing_scale = 1.0 + breathing + voice_intensity * 0.12

    # -----------------------------------------------------
    # ROTATION MATRICES
    # -----------------------------------------------------

    cx = math.cos(rotation_x)
    sx = math.sin(rotation_x)

    cy = math.cos(rotation_y)
    sy = math.sin(rotation_y)

    # -----------------------------------------------------
    # ORGANIC PARTICLE MOTION
    # -----------------------------------------------------

    movement_time = time_value * particle_speed

    movement_x = np.sin(movement_time + particle_phase) * 1.8

    movement_y = np.cos(movement_time * 0.8 + particle_phase) * 1.8

    movement_z = np.sin(movement_time * 0.6 + particle_phase * 1.3) * 1.2

    x_original = particles[:, 0] * breathing_scale

    y_original = particles[:, 1] * breathing_scale

    z_original = particles[:, 2] * breathing_scale

    x_original += movement_x
    y_original += movement_y
    z_original += movement_z

    # -----------------------------------------------------
    # ROTATE X
    # -----------------------------------------------------

    y = y_original * cx - z_original * sx

    z = y_original * sx + z_original * cx

    # -----------------------------------------------------
    # ROTATE Y
    # -----------------------------------------------------

    x = x_original * cy + z * sy

    z2 = -x_original * sy + z * cy

    # -----------------------------------------------------
    # PERSPECTIVE
    # -----------------------------------------------------

    camera_distance = 650.0

    scale = camera_distance / (camera_distance + z2)

    screen_x = x * scale + WIDTH / 2

    screen_y = y * scale + HEIGHT / 2

    # -----------------------------------------------------
    # DEPTH
    # -----------------------------------------------------

    depth = (z2 + SPHERE_RADIUS) / (SPHERE_RADIUS * 2)

    depth = np.clip(depth, 0.0, 1.0)

    # -----------------------------------------------------
    # SORT BACK → FRONT
    # -----------------------------------------------------

    order = np.argsort(z2)

    # -----------------------------------------------------
    # PARTICLES
    # -----------------------------------------------------

    for i in order:

        px = int(screen_x[i])
        py = int(screen_y[i])

        if px < -10 or px >= WIDTH + 10 or py < -10 or py >= HEIGHT + 10:
            continue

        # Front particles are brighter
        brightness = 0.20 + depth[i] * 0.80

        # Individual particle shimmer
        brightness *= 1.0 + math.sin(time_value * 2.0 + particle_phase[i]) * 0.08

        # Voice makes particles slightly more energetic
        brightness *= 1.0 + voice_intensity * 0.15

        brightness = max(0.08, min(1.15, brightness))

        color = tuple(np.clip(CORE_COLOR * brightness, 0, 255).astype(int))

        # Perspective particle size
        radius = max(1, int(0.7 + scale[i] * 1.7))

        # -------------------------------------------------
        # SUBTLE PARTICLE GLOW
        # -------------------------------------------------

        if depth[i] > 0.48:

            glow_surface = pygame.Surface(
                (radius * 6 + 2, radius * 6 + 2), pygame.SRCALPHA
            )

            center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)

            glow_radius = max(int(radius * 1.2), 3)

            pygame.draw.circle(
                glow_surface,
                (int(color[0]), int(color[1]), int(color[2]), 18),
                center,
                glow_radius,
            )

            screen.blit(
                glow_surface,
                (px - center[0], py - center[1]),
                special_flags=pygame.BLEND_ADD,
            )

        # -------------------------------------------------
        # PARTICLE
        # -------------------------------------------------

        pygame.draw.circle(screen, color, (px, py), radius)

    # =====================================================
    # DISPLAY
    # =====================================================

    pygame.display.flip()


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    for event in pygame.event.get():

        # -------------------------------------------------
        # CLOSE
        # -------------------------------------------------

        if event.type == pygame.QUIT:

            running = False

        # -------------------------------------------------
        # RESIZE
        # -------------------------------------------------

        elif event.type == pygame.VIDEORESIZE:

            WIDTH = event.w
            HEIGHT = event.h

        # -------------------------------------------------
        # MOUSE DOWN
        # -------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mouse_down = True
                last_mouse = event.pos

        # -------------------------------------------------
        # MOUSE UP
        # -------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                mouse_down = False

        # -------------------------------------------------
        # MOUSE MOVEMENT
        # -------------------------------------------------

        elif event.type == pygame.MOUSEMOTION:

            if mouse_down:

                dx = event.pos[0] - last_mouse[0]

                dy = event.pos[1] - last_mouse[1]

                rotation_y += dx * 0.008

                rotation_x += dy * 0.008

                last_mouse = event.pos

        # -------------------------------------------------
        # KEY DOWN
        # -------------------------------------------------

        elif event.type == pygame.KEYDOWN:

            # SPACE = simulated voice
            if event.key == pygame.K_SPACE:

                simulating_voice = True

            # SPACE + UP later can be expanded
            # into different intensity levels

            elif event.key == pygame.K_ESCAPE:

                running = False

        # -------------------------------------------------
        # KEY UP
        # -------------------------------------------------

        elif event.type == pygame.KEYUP:

            if event.key == pygame.K_SPACE:

                simulating_voice = False

    # =====================================================
    # SIMULATED AUDIO INTENSITY
    # =====================================================

    if simulating_voice:

        target_intensity = 1.0

    else:

        target_intensity = 0.0

    # Smooth attack/release
    voice_intensity += (target_intensity - voice_intensity) * 0.08

    # =====================================================
    # AUTOMATIC ROTATION
    # =====================================================

    if auto_rotation:

        rotation_y += 0.0025

    # =====================================================
    # TIME
    # =====================================================

    time_value += 0.016

    # =====================================================
    # DRAW
    # =====================================================

    draw_visualizer()

    clock.tick(60)


pygame.quit()
