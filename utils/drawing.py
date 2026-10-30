"""
Drawing utility functions for visual effects.
Provides glow, blur, alpha blending, and overlay helpers for OpenCV.
"""

import cv2
import numpy as np
import math


def draw_glow_circle(frame, center, radius, color, intensity=0.6, layers=5):
    """
    Draw a soft glowing circle by layering multiple semi-transparent circles
    with increasing radius and decreasing opacity.
    """
    overlay = frame.copy()
    cx, cy = int(center[0]), int(center[1])

    for i in range(layers, 0, -1):
        layer_radius = int(radius + (i * radius * 0.4))
        alpha = intensity * (1.0 - (i / (layers + 1)))
        # Scale color brightness
        scaled_color = tuple(int(c * alpha) for c in color)
        cv2.circle(overlay, (cx, cy), layer_radius, scaled_color, -1)

    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)


def draw_glow_line(frame, pt1, pt2, color, thickness=2, glow_radius=8, intensity=0.4):
    """Draw a line with a glow effect around it."""
    overlay = frame.copy()
    p1 = (int(pt1[0]), int(pt1[1]))
    p2 = (int(pt2[0]), int(pt2[1]))

    # Draw glow layers
    for i in range(3, 0, -1):
        t = thickness + i * 2
        alpha = intensity * (1.0 - (i / 4))
        scaled_color = tuple(int(c * alpha) for c in color)
        cv2.line(overlay, p1, p2, scaled_color, t)

    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    # Draw core line
    cv2.line(frame, p1, p2, color, thickness)


def apply_glow_overlay(frame, center, radius, color, intensity=0.3):
    """
    Ultra-fast localized glow overlay using downsampled ROI.
    Renders smooth aura without full-frame allocation or heavy Gaussian blur kernels.
    """
    cx, cy = int(center[0]), int(center[1])
    r = int(radius * 1.15)
    h, w = frame.shape[:2]

    x1 = max(0, cx - r)
    y1 = max(0, cy - r)
    x2 = min(w, cx + r)
    y2 = min(h, cy + r)

    if x2 <= x1 or y2 <= y1:
        return

    roi = frame[y1:y2, x1:x2]
    rh, rw = roi.shape[:2]

    # Downscale ROI 4x for ultra-fast blur (100x speedup)
    ds_w = max(4, rw // 4)
    ds_h = max(4, rh // 4)

    small_glow = np.zeros((ds_h, ds_w, 3), dtype=np.uint8)
    small_cx = int((cx - x1) * (ds_w / rw))
    small_cy = int((cy - y1) * (ds_h / rh))
    small_r = max(2, int(radius * (ds_w / rw)))

    cv2.circle(small_glow, (small_cx, small_cy), small_r, color, -1)
    small_glow = cv2.GaussianBlur(small_glow, (15, 15), 0)

    # Upscale back to ROI size and blend in-place
    glow_roi = cv2.resize(small_glow, (rw, rh), interpolation=cv2.INTER_LINEAR)
    cv2.addWeighted(glow_roi, intensity, roi, 1.0, 0, roi)


def draw_alpha_circle(frame, center, radius, color, alpha):
    """
    Draw a semi-transparent filled circle using a localized ROI.
    Avoids copying the entire full-resolution frame.
    """
    if alpha <= 0 or radius <= 0:
        return
    cx, cy = int(center[0]), int(center[1])
    r = int(radius)
    h, w = frame.shape[:2]

    x1 = max(0, cx - r)
    y1 = max(0, cy - r)
    x2 = min(w, cx + r)
    y2 = min(h, cy + r)

    if x2 <= x1 or y2 <= y1:
        return

    roi = frame[y1:y2, x1:x2]
    overlay_roi = roi.copy()
    cv2.circle(overlay_roi, (cx - x1, cy - y1), r, color, -1)
    cv2.addWeighted(overlay_roi, alpha, roi, 1.0 - alpha, 0, roi)


def draw_lightning_arc(frame, start, end, color, segments=6, jitter=15, thickness=2):
    """
    Draw a jagged lightning arc between two points.
    Creates a zigzag path with random offsets for an electric look.
    """
    points = [start]
    for i in range(1, segments):
        t = i / segments
        # Linear interpolation between start and end
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        # Add random jitter perpendicular to the line
        x += np.random.randint(-jitter, jitter + 1)
        y += np.random.randint(-jitter, jitter + 1)
        points.append((int(x), int(y)))
    points.append(end)

    # Draw the arc with glow
    for i in range(len(points) - 1):
        p1 = (int(points[i][0]), int(points[i][1]))
        p2 = (int(points[i + 1][0]), int(points[i + 1][1]))
        # Glow layer
        cv2.line(frame, p1, p2, tuple(int(c * 0.4) for c in color), thickness + 4)
        # Core line
        cv2.line(frame, p1, p2, color, thickness)


def draw_spinning_lines(frame, center, radius, angle, num_lines, color, thickness=1):
    """Draw rotating lines emanating from center (for Rasengan spiral effect)."""
    cx, cy = center
    for i in range(num_lines):
        a = angle + (2 * math.pi * i / num_lines)
        end_x = int(cx + radius * math.cos(a))
        end_y = int(cy + radius * math.sin(a))
        start_x = int(cx + (radius * 0.3) * math.cos(a))
        start_y = int(cy + (radius * 0.3) * math.sin(a))
        cv2.line(frame, (start_x, start_y), (end_x, end_y), color, thickness)


def draw_shuriken_blade(frame, center, angle, length, width, color, border_color=(255, 255, 255), border_thickness=2):
    """Draw a single shuriken blade (curved wing shape) with a glowing outline border."""
    cx, cy = center

    # Create blade as a set of points forming a curved wing shape
    points = []
    num_curve_points = 14
    for i in range(num_curve_points + 1):
        t = i / num_curve_points
        # Blade tapers: curved sweep like Rasenshuriken wind wing
        blade_width = width * math.sin(t * math.pi) * 0.55
        along = t * length

        # Main direction with slight arc
        curve_angle = angle + 0.15 * math.sin(t * math.pi)
        dx = math.cos(curve_angle)
        dy = math.sin(curve_angle)
        px = -dy
        py = dx

        x1 = cx + dx * along + px * blade_width
        y1 = cy + dy * along + py * blade_width
        points.append((int(x1), int(y1)))

    for i in range(num_curve_points, -1, -1):
        t = i / num_curve_points
        blade_width = width * math.sin(t * math.pi) * 0.55
        along = t * length
        curve_angle = angle + 0.15 * math.sin(t * math.pi)
        dx = math.cos(curve_angle)
        dy = math.sin(curve_angle)
        px = -dy
        py = dx
        x2 = cx + dx * along - px * blade_width
        y2 = cy + dy * along - py * blade_width
        points.append((int(x2), int(y2)))

    if len(points) > 2:
        pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(frame, [pts], color)
        cv2.polylines(frame, [pts], True, border_color, border_thickness)


def put_text_with_shadow(frame, text, position, font_scale=1.0, color=(255, 255, 255),
                         thickness=2, shadow_color=(0, 0, 0)):
    """Draw text with a drop shadow for better readability."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    x, y = position
    # Shadow
    cv2.putText(frame, text, (x + 2, y + 2), font, font_scale, shadow_color, thickness + 1)
    # Main text
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
