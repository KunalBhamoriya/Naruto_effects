"""
Rasengan visual effect — Glowing blue orb with swirling particles.
"""

import cv2
import math
import numpy as np

import config
from effects.base_effect import BaseEffect
from effects.particle import ParticleSystem
from utils.drawing import draw_glow_circle, apply_glow_overlay, draw_spinning_lines, draw_alpha_circle
from utils.math_utils import lerp, lerp_point


class RasenganEffect(BaseEffect):
    """
    Rasengan: A spinning blue energy sphere held in the palm.

    Visual layers:
    1. Outer glow (large, soft, blue)
    2. Swirling orbital particles
    3. Inner spinning lines (spiral effect)
    4. Core bright circle (pulsating)
    5. Center white-hot point
    """

    def __init__(self):
        super().__init__()
        self.particles = ParticleSystem(max_particles=config.RASENGAN_NUM_PARTICLES * 2)
        self.angle = 0.0
        self.pulse_phase = 0.0
        self.target_center = (0, 0)
        self.smooth_center = (0, 0)
        self.initialized = False

    def update(self, palm_centers, fingertips, frame_shape):
        """Update Rasengan position, particles, and animation state."""
        self.frame_count += 1
        self.update_opacity(config.EFFECT_FADE_IN_SPEED, config.EFFECT_FADE_OUT_SPEED)

        if not self.is_visible():
            self.particles.clear()
            return

        # Update center position (smooth tracking)
        if palm_centers:
            self.target_center = palm_centers[0]
            if not self.initialized:
                self.smooth_center = self.target_center
                self.initialized = True
            else:
                self.smooth_center = lerp_point(
                    self.smooth_center, self.target_center, config.POSITION_SMOOTHING
                )

        cx, cy = self.smooth_center

        # Update animation
        self.angle += config.RASENGAN_ORBIT_SPEED
        self.pulse_phase += config.RASENGAN_PULSE_SPEED

        # Spawn orbiting particles
        if self.frame_count % 2 == 0:
            orbit_radius = config.RASENGAN_BASE_RADIUS * 0.85
            num_spawn = 4
            for i in range(num_spawn):
                a = self.angle + (2 * math.pi * i / num_spawn) + np.random.uniform(-0.3, 0.3)
                px = cx + orbit_radius * math.cos(a)
                py = cy + orbit_radius * math.sin(a)
                # Tangential velocity
                vx = -math.sin(a) * 2.2 + np.random.uniform(-0.5, 0.5)
                vy = math.cos(a) * 2.2 + np.random.uniform(-0.5, 0.5)

                # Vary blue shades
                color_var = np.random.randint(-25, 25)
                color = tuple(
                    max(0, min(255, c + color_var))
                    for c in config.RASENGAN_PARTICLE_COLOR
                )
                size = np.random.randint(2, 5)
                self.particles.spawn(px, py, vx, vy, color, size, lifetime=28)

        # Spawn some outward-drifting particles
        if self.frame_count % 4 == 0:
            self.particles.spawn_burst(
                cx, cy, count=3, speed=1.8,
                color=config.RASENGAN_PARTICLE_COLOR,
                size_range=(1, 3), lifetime=22
            )

        self.particles.update()

    def render(self, frame):
        """Render the Rasengan effect onto the frame."""
        if not self.is_visible():
            return

        cx, cy = int(self.smooth_center[0]), int(self.smooth_center[1])
        opacity = self.opacity

        # Pulsating radius
        pulse = math.sin(self.pulse_phase) * config.RASENGAN_PULSE_AMPLITUDE
        base_r = config.RASENGAN_BASE_RADIUS + pulse

        # Layer 1: Outer glow (soft white-blue aura)
        apply_glow_overlay(
            frame,
            self.smooth_center,
            config.RASENGAN_GLOW_RADIUS + pulse,
            config.RASENGAN_OUTER_COLOR,
            intensity=0.28 * opacity
        )

        # Layer 2: Orbital chakra particles (Blue)
        self.particles.render(frame, global_opacity=opacity)

        # Layer 3: Middle body - semi-transparent rich blue sphere
        draw_alpha_circle(frame, (cx, cy), int(base_r), config.RASENGAN_MID_COLOR, 0.45 * opacity)

        # Layer 4: Dense spinning chakra spiral lines in the middle
        draw_spinning_lines(
            frame,
            (cx, cy),
            int(base_r * 0.95),
            self.angle,
            num_lines=10,
            color=tuple(int(c * opacity * 0.85) for c in config.RASENGAN_CORE_COLOR),
            thickness=2
        )

        # Layer 5: Vivid blue center sphere
        inner_r = int(base_r * 0.6)
        draw_alpha_circle(frame, (cx, cy), inner_r, config.RASENGAN_CORE_COLOR, 0.65 * opacity)

        # Deep concentrated blue core vortex point
        cv2.circle(frame, (cx, cy), max(3, int(inner_r * 0.35)),
                   (255, 80, 0), -1)

        # Layer 6: Crisp White Outer Border
        white_border_color = tuple(int(c * opacity) for c in config.RASENGAN_BORDER_COLOR)
        # Inner solid border
        cv2.circle(frame, (cx, cy), int(base_r), white_border_color, max(2, int(3 * opacity)))
        # Outer soft border glow ring
        cv2.circle(frame, (cx, cy), int(base_r + 1), (255, 255, 255), 1)

        # Layer 7: Spinning white rim arcs along the border
        for i in range(4):
            a = self.angle * 2.5 + (2 * math.pi * i / 4)
            arc_start = int(math.degrees(a)) % 360
            arc_end = (arc_start + 45) % 360
            cv2.ellipse(frame, (cx, cy), (int(base_r), int(base_r)),
                        0, arc_start, arc_end,
                        white_border_color, max(2, int(3 * opacity)))

    def deactivate(self):
        """Deactivate and reset initialization flag."""
        super().deactivate()
        self.initialized = False
