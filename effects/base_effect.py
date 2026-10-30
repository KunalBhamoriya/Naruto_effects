"""
Base effect class and particle system for visual effects.
"""

from abc import ABC, abstractmethod


class BaseEffect(ABC):
    """Abstract base class for all jutsu visual effects."""

    def __init__(self):
        self.active = False
        self.opacity = 0.0  # 0.0 = invisible, 1.0 = full effect
        self.frame_count = 0

    @abstractmethod
    def update(self, palm_centers, fingertips, frame_shape):
        """
        Update the effect state for the current frame.

        Args:
            palm_centers: List of (x, y) palm center positions.
            fingertips: List of fingertip positions per hand.
            frame_shape: (height, width, channels) of the frame.
        """
        pass

    @abstractmethod
    def render(self, frame):
        """
        Render the effect onto the frame.

        Args:
            frame: The OpenCV BGR frame to draw on (modified in-place).
        """
        pass

    def activate(self):
        """Start showing this effect."""
        self.active = True

    def deactivate(self):
        """Start fading out this effect."""
        self.active = False

    def update_opacity(self, fade_in_speed=0.08, fade_out_speed=0.12):
        """Smoothly transition opacity based on active state."""
        if self.active:
            self.opacity = min(1.0, self.opacity + fade_in_speed)
        else:
            self.opacity = max(0.0, self.opacity - fade_out_speed)

    def is_visible(self):
        """Check if the effect has any opacity (should be rendered)."""
        return self.opacity > 0.01
