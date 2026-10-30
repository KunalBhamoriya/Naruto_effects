"""
Math utility functions for gesture recognition and visual effects.
Provides vector operations, angle calculations, and distance helpers.
"""

import numpy as np
import math


def distance(p1, p2):
    """Calculate Euclidean distance between two points (x, y)."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def midpoint(p1, p2):
    """Calculate midpoint between two points."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def angle_between(p1, p2, p3):
    """
    Calculate the angle at p2 formed by the line segments p1-p2 and p2-p3.
    Returns angle in degrees (0-180).
    """
    v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
    v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])

    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return np.degrees(np.arccos(cos_angle))


def lerp(a, b, t):
    """Linear interpolation between a and b by factor t (0.0 to 1.0)."""
    return a + (b - a) * t


def lerp_point(p1, p2, t):
    """Linear interpolation between two points."""
    return (lerp(p1[0], p2[0], t), lerp(p1[1], p2[1], t))


def random_point_in_circle(center, radius):
    """Generate a random point within a circle."""
    angle = np.random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(np.random.uniform(0, 1))
    return (center[0] + r * math.cos(angle), center[1] + r * math.sin(angle))


def random_point_on_circle(center, radius):
    """Generate a random point on the circumference of a circle."""
    angle = np.random.uniform(0, 2 * math.pi)
    return (center[0] + radius * math.cos(angle),
            center[1] + radius * math.sin(angle))


def normalize_vector(v):
    """Normalize a 2D vector to unit length."""
    length = math.sqrt(v[0] ** 2 + v[1] ** 2) + 1e-6
    return (v[0] / length, v[1] / length)


def rotate_point(point, center, angle_rad):
    """Rotate a point around a center by the given angle (radians)."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    return (
        center[0] + dx * cos_a - dy * sin_a,
        center[1] + dx * sin_a + dy * cos_a
    )


def clamp(value, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))
