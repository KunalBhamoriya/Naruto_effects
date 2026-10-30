"""
Chidori visual effect — Crackling lightning and electric arcs.
"""

import cv2
import math
import numpy as np

import config
from effects.base_effect import BaseEffect
from effects.particle import ParticleSystem
from utils.drawing import draw_lightning_arc, apply_glow_overlay, draw_alpha_circle
from utils.math_utils import lerp_point, random_point_in_circle


class ChidoriEffect(BaseEffect):
    """
    Chidori: Crackling lightning energy concentrated in the hand.

    Visual layers:
    1. Purple-blue glow aura around the hand
    2. Multiple branching lightning arcs from fingertips
    3. Flickering bright core at palm center
    4. Spark particles flying off randomly
    5. Occasional screen-edge flash
    """

    def __init__(self):
        super().__init__()
        self.sparks = ParticleSystem(max_particles=config.CHIDORI_SPARK_COUNT * 3)
        self.arcs = []  # List of (start, end) tuples for lightning arcs
        self.target_center = (0, 0)
        self.smooth_center = (0, 0)
        self.target_fingertips = []
        self.smooth_fingertips = []
        self.initialized = False
        self.flash_intensity = 0.0

    def _generate_arcs(self, center, fingertips):
        """Generate random lightning arc endpoints."""
        self.arcs.clear()
        cx, cy = center

        # Arcs from palm center to fingertips and outward
        for tip in fingertips[:2]:  # Extended fingers
            # Arc to the fingertip
            self.arcs.append((
                (int(cx), int(cy)),
                (int(tip[0]) + np.random.randint(-12, 13),
                 int(tip[1]) + np.random.randint(-12, 13))
            ))
            # 2 Branching arcs from each fingertip outward
            for _ in range(2):
                angle = np.random.uniform(0, 2 * math.pi)
                length = np.random.randint(60, config.CHIDORI_ARC_MAX_LENGTH)
                end_x = int(tip[0] + length * math.cos(angle))
                end_y = int(tip[1] + length * math.sin(angle))
                self.arcs.append(((int(tip[0]), int(tip[1])), (end_x, end_y)))

        # Random arcs crackling outward from the hand
        for _ in range(config.CHIDORI_NUM_ARCS - 6):
            angle = np.random.uniform(0, 2 * math.pi)
            start_r = np.random.randint(10, 45)
            end_r = np.random.randint(70, config.CHIDORI_ARC_MAX_LENGTH)
            start = (int(cx + start_r * math.cos(angle)),
                     int(cy + start_r * math.sin(angle)))
            end = (int(cx + end_r * math.cos(angle + np.random.uniform(-0.6, 0.6))),
                   int(cy + end_r * math.sin(angle + np.random.uniform(-0.6, 0.6))))
            self.arcs.append((start, end))

    def update(self, palm_centers, fingertips, frame_shape):
        """Update Chidori effect state."""
        self.frame_count += 1
        self.update_opacity(config.EFFECT_FADE_IN_SPEED, config.EFFECT_FADE_OUT_SPEED)

        if not self.is_visible():
            self.sparks.clear()
            self.arcs.clear()
            return

        # Smooth position tracking
        if palm_centers:
            self.target_center = palm_centers[0]
            if fingertips:
                self.target_fingertips = fingertips[0]

            if not self.initialized:
                self.smooth_center = self.target_center
                self.smooth_fingertips = list(self.target_fingertips) if self.target_fingertips else []
                self.initialized = True
            else:
                self.smooth_center = lerp_point(
                    self.smooth_center, self.target_center, config.POSITION_SMOOTHING
                )
                if self.target_fingertips and self.smooth_fingertips:
                    self.smooth_fingertips = [
                        lerp_point(s, t, config.POSITION_SMOOTHING)
                        for s, t in zip(self.smooth_fingertips, self.target_fingertips)
                    ]
                else:
                    self.smooth_fingertips = list(self.target_fingertips)

        cx, cy = self.smooth_center

        # Regenerate arcs rapidly for high-voltage flickering effect
        if self.frame_count % config.CHIDORI_FLICKER_RATE == 0:
            tips = self.smooth_fingertips if self.smooth_fingertips else []
            self._generate_arcs(self.smooth_center, tips)

        # Spawn vibrant electric blue spark particles
        if self.frame_count % 2 == 0:
            for _ in range(6):
                angle = np.random.uniform(0, 2 * math.pi)
                speed = np.random.uniform(3.5, 8.0)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                spawn_pos = random_point_in_circle(self.smooth_center, 45)
                color_var = np.random.randint(-20, 20)
                color = tuple(
                    max(0, min(255, c + color_var))
                    for c in config.CHIDORI_SPARK_COLOR
                )
                self.sparks.spawn(spawn_pos[0], spawn_pos[1], vx, vy,
                                  color, size=np.random.randint(1, 4), lifetime=18)

        # Flash effect (random high-energy electrical bursts)
        if np.random.random() < 0.12:
            self.flash_intensity = 0.22
        self.flash_intensity = max(0, self.flash_intensity - 0.04)

        self.sparks.update()

    def render(self, frame):
        """Render the Chidori effect onto the frame."""
        if not self.is_visible():
            return

        cx, cy = int(self.smooth_center[0]), int(self.smooth_center[1])
        opacity = self.opacity

        # Layer 1: Electric Blue Glow Aura
        apply_glow_overlay(
            frame,
            self.smooth_center,
            config.CHIDORI_GLOW_RADIUS,
            config.CHIDORI_GLOW_COLOR,
            intensity=0.36 * opacity
        )

        # Layer 2: Crackling Electric Blue Lightning Arcs
        for start, end in self.arcs:
            jitter = np.random.randint(12, 26)
            arc_color = tuple(int(c * opacity) for c in config.CHIDORI_ARC_COLOR)
            draw_lightning_arc(
                frame, start, end, arc_color,
                segments=config.CHIDORI_ARC_SEGMENTS,
                jitter=jitter,
                thickness=np.random.randint(2, 4)
            )

        # Layer 3: Enlarged bright flickering electrical core
        core_radius = np.random.randint(30, 52)

        # Outer electric blue corona
        draw_alpha_circle(frame, (cx, cy), int(core_radius * 1.35), config.CHIDORI_ARC_COLOR, 0.45 * opacity)

        # Hot white electrical core
        draw_alpha_circle(frame, (cx, cy), core_radius, config.CHIDORI_CORE_COLOR, 0.65 * opacity)

        # Intense white center point
        cv2.circle(frame, (cx, cy), max(4, int(core_radius * 0.45)),
                   (255, 255, 255), -1)

        # Layer 4: Electric spark particles
        self.sparks.render(frame, global_opacity=opacity)

        # Layer 5: Screen flash effect
        if self.flash_intensity > 0:
            flash_overlay = np.zeros_like(frame)
            flash_overlay[:] = config.CHIDORI_ARC_COLOR
            cv2.addWeighted(flash_overlay, self.flash_intensity * opacity,
                            frame, 1.0, 0, frame)

        # Layer 6: Glowing white electric discharge nodes along arcs
        for start, end in self.arcs:
            if np.random.random() < 0.6:
                t = np.random.uniform(0.2, 0.8)
                dot_x = int(start[0] + (end[0] - start[0]) * t)
                dot_y = int(start[1] + (end[1] - start[1]) * t)
                cv2.circle(frame, (dot_x, dot_y), 3, (255, 255, 255), -1)
                cv2.circle(frame, (dot_x, dot_y), 5, config.CHIDORI_ARC_COLOR, 1)

    def deactivate(self):
        """Deactivate and reset."""
        super().deactivate()
        self.initialized = False
