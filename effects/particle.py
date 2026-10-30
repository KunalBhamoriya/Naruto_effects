"""
Particle system for visual effects.
Manages creation, physics, rendering, and lifecycle of particles.
"""

import numpy as np
import math
import cv2
import config


class Particle:
    """A single particle with position, velocity, color, and lifetime."""

    __slots__ = ['x', 'y', 'vx', 'vy', 'color', 'size', 'lifetime', 'max_lifetime', 'alpha']

    def __init__(self, x, y, vx, vy, color, size=2, lifetime=30):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alpha = 1.0

    def update(self):
        """Update particle position and age."""
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        # Fade out near end of life
        life_ratio = self.lifetime / self.max_lifetime
        if life_ratio < config.PARTICLE_FADE_START:
            self.alpha = life_ratio / config.PARTICLE_FADE_START

    def is_alive(self):
        """Check if particle still has lifetime remaining."""
        return self.lifetime > 0


class ParticleSystem:
    """Manages a collection of particles with spawning, updating, and rendering."""

    def __init__(self, max_particles=100):
        self.particles = []
        self.max_particles = max_particles

    def spawn(self, x, y, vx, vy, color, size=2, lifetime=None):
        """Spawn a new particle if under the limit."""
        if len(self.particles) >= self.max_particles:
            return
        if lifetime is None:
            lifetime = config.PARTICLE_MAX_LIFETIME
        self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))

    def spawn_burst(self, x, y, count, speed, color, size_range=(1, 4), lifetime=None):
        """Spawn a burst of particles in random directions."""
        for _ in range(count):
            angle = np.random.uniform(0, 2 * math.pi)
            spd = np.random.uniform(speed * 0.5, speed)
            vx = spd * math.cos(angle)
            vy = spd * math.sin(angle)
            size = np.random.randint(size_range[0], size_range[1] + 1)
            self.spawn(x, y, vx, vy, color, size, lifetime)

    def spawn_orbit(self, center_x, center_y, radius, count, color,
                    orbit_speed=0.05, size_range=(1, 3), angle_offset=0, lifetime=None):
        """Spawn particles in an orbital pattern around a center point."""
        for i in range(count):
            angle = angle_offset + (2 * math.pi * i / count)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            # Velocity tangent to the orbit
            vx = -orbit_speed * radius * math.sin(angle) * 0.1
            vy = orbit_speed * radius * math.cos(angle) * 0.1
            size = np.random.randint(size_range[0], size_range[1] + 1)
            self.spawn(x, y, vx, vy, color, size, lifetime)

    def update(self):
        """Update all particles and remove dead ones."""
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive()]

    def render(self, frame, global_opacity=1.0):
        """Render all particles onto the frame."""
        for p in self.particles:
            alpha = p.alpha * global_opacity
            if alpha < 0.05:
                continue

            # Scale color by alpha
            color = tuple(int(c * alpha) for c in p.color)
            cx, cy = int(p.x), int(p.y)
            size = max(1, int(p.size * alpha))

            if size <= 1:
                # Just set pixel for tiny particles
                h, w = frame.shape[:2]
                if 0 <= cx < w and 0 <= cy < h:
                    frame[cy, cx] = [
                        min(255, frame[cy, cx][0] + color[0]),
                        min(255, frame[cy, cx][1] + color[1]),
                        min(255, frame[cy, cx][2] + color[2]),
                    ]
            else:
                cv2.circle(frame, (cx, cy), size, color, -1)

    def clear(self):
        """Remove all particles."""
        self.particles.clear()

    def count(self):
        """Get current particle count."""
        return len(self.particles)
