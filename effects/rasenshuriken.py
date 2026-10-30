"""
Rasenshuriken visual effect — Giant spinning wind shuriken between both hands.
"""

import cv2
import math
import numpy as np

import config
from effects.base_effect import BaseEffect
from effects.particle import ParticleSystem
from utils.drawing import (
    apply_glow_overlay, draw_glow_circle, draw_shuriken_blade, draw_spinning_lines, draw_alpha_circle
)
from utils.math_utils import lerp_point, midpoint, distance, rotate_point


class RasenshurikenEffect(BaseEffect):
    """
    Rasenshuriken: A massive wind-infused shuriken spinning between both hands.

    Visual layers:
    1. Outer green-white glow
    2. Four spinning wind blades
    3. Wind spiral particles
    4. Central Rasengan-like orb (smaller, green tinted)
    5. Distortion ring effect
    """

    def __init__(self):
        super().__init__()
        self.wind_particles = ParticleSystem(
            max_particles=config.RASENSHURIKEN_WIND_PARTICLES * 3
        )
        self.angle = 0.0
        self.pulse_phase = 0.0
        self.target_center = (0, 0)
        self.smooth_center = (0, 0)
        self.target_scale = 1.0
        self.smooth_scale = 1.0
        self.initialized = False
        self.expansion_phase = 0.0

    def update(self, palm_centers, fingertips, frame_shape):
        """Update Rasenshuriken effect state."""
        self.frame_count += 1
        self.update_opacity(config.EFFECT_FADE_IN_SPEED * 0.8,
                            config.EFFECT_FADE_OUT_SPEED)

        if not self.is_visible():
            self.wind_particles.clear()
            return

        # Calculate center between both hands
        if len(palm_centers) >= 2:
            self.target_center = midpoint(palm_centers[0], palm_centers[1])
            hand_dist = distance(palm_centers[0], palm_centers[1])
            self.target_scale = max(0.5, min(2.0, hand_dist / 200.0))
        elif palm_centers:
            self.target_center = palm_centers[0]
            self.target_scale = 1.0

        if not self.initialized:
            self.smooth_center = self.target_center
            self.smooth_scale = self.target_scale
            self.initialized = True
        else:
            self.smooth_center = lerp_point(
                self.smooth_center, self.target_center, config.POSITION_SMOOTHING
            )
            self.smooth_scale += (self.target_scale - self.smooth_scale) * config.POSITION_SMOOTHING

        cx, cy = self.smooth_center
        scale = self.smooth_scale

        # Update animation
        self.angle -= config.RASENSHURIKEN_SPIN_SPEED  # Counter-clockwise
        self.pulse_phase += 0.1
        self.expansion_phase += 0.05

        # Spawn wind spiral particles
        if self.frame_count % 2 == 0:
            blade_length = config.RASENSHURIKEN_BLADE_LENGTH * scale
            for i in range(4):
                # Particles along blade edges
                blade_angle = self.angle + (math.pi / 2 * i)
                t = np.random.uniform(0.3, 1.0)
                px = cx + blade_length * t * math.cos(blade_angle)
                py = cy + blade_length * t * math.sin(blade_angle)

                # Tangential velocity (wind swirl)
                speed = np.random.uniform(1.0, 3.0)
                vx = -speed * math.sin(blade_angle) + np.random.uniform(-1, 1)
                vy = speed * math.cos(blade_angle) + np.random.uniform(-1, 1)

                color_var = np.random.randint(-20, 20)
                color = tuple(
                    max(0, min(255, c + color_var))
                    for c in config.RASENSHURIKEN_WIND_COLOR
                )
                self.wind_particles.spawn(px, py, vx, vy, color,
                                          size=np.random.randint(1, 3),
                                          lifetime=20)

        # Spawn outward spiral particles
        if self.frame_count % 3 == 0:
            for _ in range(3):
                a = np.random.uniform(0, 2 * math.pi)
                r = np.random.uniform(10, 30) * scale
                px = cx + r * math.cos(a)
                py = cy + r * math.sin(a)
                speed = np.random.uniform(1.5, 3.0)
                vx = speed * math.cos(a)
                vy = speed * math.sin(a)
                self.wind_particles.spawn(
                    px, py, vx, vy,
                    config.RASENSHURIKEN_WIND_COLOR,
                    size=np.random.randint(1, 3),
                    lifetime=25
                )

        self.wind_particles.update()

    def render(self, frame):
        """Render the Rasenshuriken effect onto the frame."""
        if not self.is_visible():
            return

        cx, cy = int(self.smooth_center[0]), int(self.smooth_center[1])
        opacity = self.opacity
        scale = self.smooth_scale

        blade_length = config.RASENSHURIKEN_BLADE_LENGTH * scale
        blade_width = config.RASENSHURIKEN_BLADE_WIDTH * scale
        core_radius = config.RASENSHURIKEN_CORE_RADIUS * scale
        white_color = tuple(int(c * opacity) for c in config.RASENSHURIKEN_BORDER_COLOR)

        # Layer 1: Outer glow (Brilliant white-blue aura)
        glow_r = config.RASENSHURIKEN_GLOW_RADIUS * scale
        apply_glow_overlay(
            frame,
            self.smooth_center,
            glow_r,
            config.RASENSHURIKEN_GLOW_COLOR,
            intensity=0.28 * opacity
        )

        # Layer 2: White wind distortion rings (concentric expanding shockwaves)
        expansion = math.sin(self.expansion_phase) * 0.3 + 0.7
        for i in range(3):
            ring_r = int((core_radius + blade_length * 0.32 * (i + 1)) * expansion)
            ring_color = tuple(int(255 * opacity * (0.5 - i * 0.12)) for _ in range(3))
            cv2.circle(frame, (cx, cy), ring_r, ring_color, 2)

        # Layer 3: Four spinning wind blades (Pure white with crisp solid white borders)
        blade_fill_color = tuple(int(c * opacity * 0.8) for c in config.RASENSHURIKEN_BLADE_COLOR)
        for i in range(config.RASENSHURIKEN_NUM_BLADES):
            blade_angle = self.angle + (2 * math.pi * i / config.RASENSHURIKEN_NUM_BLADES)
            draw_shuriken_blade(
                frame,
                (cx, cy),
                blade_angle,
                int(blade_length),
                int(blade_width),
                blade_fill_color,
                border_color=white_color,
                border_thickness=max(2, int(3 * opacity))
            )

        # Layer 4: Wind spiral particles
        self.wind_particles.render(frame, global_opacity=opacity)

        # Layer 5: Central Blue Orb (Blue in middle, like Rasengan core)
        draw_alpha_circle(frame, (cx, cy), int(core_radius), config.RASENSHURIKEN_CORE_COLOR, 0.55 * opacity)

        # Inner spinning chakra turbulence lines (vivid blue)
        draw_spinning_lines(
            frame,
            (cx, cy),
            int(core_radius * 0.95),
            self.angle * 3.5,
            num_lines=10,
            color=tuple(int(c * opacity * 0.9) for c in (255, 80, 0)),
            thickness=2
        )

        # Concentrated deep blue center core
        inner_r = max(4, int(core_radius * 0.5))
        cv2.circle(frame, (cx, cy), inner_r, (255, 110, 10), -1)
        cv2.circle(frame, (cx, cy), max(2, int(inner_r * 0.4)), (255, 60, 0), -1)

        # Crisp White Border on the Central Orb
        cv2.circle(frame, (cx, cy), int(core_radius), white_color, max(2, int(3 * opacity)))
        cv2.circle(frame, (cx, cy), int(core_radius + 1), (255, 255, 255), 1)

        # Layer 6: Glowing white blade tips
        for i in range(config.RASENSHURIKEN_NUM_BLADES):
            blade_angle = self.angle + (2 * math.pi * i / config.RASENSHURIKEN_NUM_BLADES)
            tip_x = int(cx + blade_length * math.cos(blade_angle))
            tip_y = int(cy + blade_length * math.sin(blade_angle))

            # Brilliant white tip flare
            cv2.circle(frame, (tip_x, tip_y), max(4, int(6 * scale)), (255, 255, 255), -1)
            cv2.circle(frame, (tip_x, tip_y), max(7, int(12 * scale)), (255, 240, 210), 2)

    def deactivate(self):
        """Deactivate and reset."""
        super().deactivate()
        self.initialized = False
