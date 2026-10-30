"""
Hand detection wrapper using MediaPipe Hand Landmarker (Tasks API).
Extracts hand landmarks and provides convenient access to landmark positions.
"""

import cv2
import mediapipe as mp
import os
import config

# MediaPipe Tasks API imports
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


class HandDetector:
    """Wrapper around MediaPipe Hand Landmarker for detecting and tracking hand landmarks."""

    # MediaPipe hand landmark indices (same as legacy API)
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20

    # Hand connections for drawing (pairs of landmark indices)
    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),          # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),           # Index
        (0, 9), (9, 10), (10, 11), (11, 12),      # Middle  (wrist→MCP via 0→9)
        (0, 13), (13, 14), (14, 15), (15, 16),    # Ring
        (0, 17), (17, 18), (18, 19), (19, 20),    # Pinky
        (5, 9), (9, 13), (13, 17),                 # Palm
    ]

    def __init__(self):
        # Locate model file
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hand_landmarker.task')
        model_path = os.path.normpath(model_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Hand landmarker model not found at: {model_path}\n"
                "Download it from: https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
            )

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=config.MAX_NUM_HANDS,
            min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.last_results = None
        self._timestamp_ms = 0

    def detect(self, frame):
        """
        Detect hands in the given frame.

        Args:
            frame: BGR image from OpenCV.

        Returns:
            List of detected hands, where each hand is a list of (x, y) tuples
            in pixel coordinates for all 21 landmarks.
        """
        h, w, _ = frame.shape

        # Convert BGR -> RGB and downscale to 640x360 for high-speed inference
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        small_rgb = cv2.resize(rgb_frame, (640, 360), interpolation=cv2.INTER_NEAREST)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=small_rgb)

        # Increment timestamp (must be monotonically increasing for VIDEO mode)
        self._timestamp_ms += 33  # ~30 FPS
        self.last_results = self.landmarker.detect_for_video(mp_image, self._timestamp_ms)

        hands_data = []
        if self.last_results.hand_landmarks:
            for hand_landmarks in self.last_results.hand_landmarks:
                landmarks = []
                for lm in hand_landmarks:
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    landmarks.append((x, y))
                hands_data.append(landmarks)

        return hands_data

    def draw_landmarks(self, frame):
        """Draw hand landmarks and connections on the frame."""
        if not self.last_results or not self.last_results.hand_landmarks:
            return

        h, w, _ = frame.shape
        for hand_landmarks in self.last_results.hand_landmarks:
            # Convert normalized landmarks to pixel coordinates
            points = []
            for lm in hand_landmarks:
                x = int(lm.x * w)
                y = int(lm.y * h)
                points.append((x, y))

            # Draw connections
            for start_idx, end_idx in self.HAND_CONNECTIONS:
                cv2.line(frame, points[start_idx], points[end_idx], (0, 200, 80), 1)

            # Draw landmark points
            for px, py in points:
                cv2.circle(frame, (px, py), 3, (0, 255, 100), -1)
                cv2.circle(frame, (px, py), 3, (0, 200, 80), 1)

    @staticmethod
    def get_palm_center(landmarks):
        """
        Calculate the center of the palm from landmarks.
        Uses the average of wrist, index MCP, middle MCP, ring MCP, and pinky MCP.
        """
        palm_points = [
            landmarks[HandDetector.WRIST],
            landmarks[HandDetector.INDEX_MCP],
            landmarks[HandDetector.MIDDLE_MCP],
            landmarks[HandDetector.RING_MCP],
            landmarks[HandDetector.PINKY_MCP],
        ]
        cx = sum(p[0] for p in palm_points) / len(palm_points)
        cy = sum(p[1] for p in palm_points) / len(palm_points)
        return (cx, cy)

    @staticmethod
    def get_palm_size(landmarks):
        """
        Estimate palm size as the distance from wrist to middle finger MCP.
        Used as a reference distance for gesture detection thresholds.
        """
        from utils.math_utils import distance
        return distance(landmarks[HandDetector.WRIST], landmarks[HandDetector.MIDDLE_MCP])

    @staticmethod
    def get_fingertip_positions(landmarks):
        """Return positions of all 5 fingertips."""
        return [
            landmarks[HandDetector.THUMB_TIP],
            landmarks[HandDetector.INDEX_TIP],
            landmarks[HandDetector.MIDDLE_TIP],
            landmarks[HandDetector.RING_TIP],
            landmarks[HandDetector.PINKY_TIP],
        ]

    def close(self):
        """Release MediaPipe resources."""
        self.landmarker.close()
